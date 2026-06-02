import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import cabecera from "../../assets/cabecera.png";
import "../../styles/partidas.css";

const ESTADO_LABELS = {
	en_juego: "En juego",
	sala_espera: "Sala de espera",
	desconocido: "Desconocido",
};

const ESTADO_CLASS = {
	en_juego: "partidas-status partidas-status--en-juego",
	sala_espera: "partidas-status partidas-status--sala-espera",
	desconocido: "partidas-status partidas-status--desconocido",
};

function getEstadoLabel(estado) {
	if (!estado) return ESTADO_LABELS.desconocido;
	return ESTADO_LABELS[estado] ?? ESTADO_LABELS.desconocido;
}

function getEstadoClass(estado) {
	if (!estado) return ESTADO_CLASS.desconocido;
	return ESTADO_CLASS[estado] ?? ESTADO_CLASS.desconocido;
}

export default function ListaPartidas() {
	const navigate = useNavigate();
	const [partidas, setPartidas] = useState([]);
	const [page, setPage] = useState(1);
	const [totalPages, setTotalPages] = useState(1);
	const [totalPartidas, setTotalPartidas] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [search, setSearch] = useState("");

	const loadPartidas = useCallback((pageNumber = 1) => {
		let cancelled = false;
		setLoading(true);
		setError("");

		fetch(`/api/partidas/publicas/?page=${pageNumber}`, {
			method: "GET",
			credentials: "include",
		})
			.then(async (res) => {
				const data = await res.json().catch(() => ({}));
				if (cancelled) return;
				if (!res.ok) {
					const detail = data?.detail || "No se pudo cargar la lista de partidas";
					throw new Error(detail);
				}
				const items = Array.isArray(data?.items) ? data.items : [];

				if (cancelled) return;
				setPartidas(items);
				setPage(typeof data?.page === "number" ? data.page : pageNumber);
				setTotalPages(typeof data?.total_pages === "number" ? data.total_pages : 1);
				setTotalPartidas(typeof data?.total === "number" ? data.total : 0);
			})
			.catch((e) => {
				if (cancelled) return;
				setError(e instanceof Error ? e.message : "Error cargando partidas");
				setPartidas([]);
				setTotalPartidas(0);
				setTotalPages(1);
			})
			.finally(() => {
				if (cancelled) return;
				setLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, []);

	useEffect(() => {
		const cancel = loadPartidas(page);
		return () => {
			if (typeof cancel === "function") cancel();
		};
	}, [loadPartidas, page]);

	const filteredPartidas = useMemo(() => {
		const normalized = search.trim().toLowerCase();
		if (!normalized) return partidas;

		return partidas.filter((partida) => {
			const nombre = `${partida?.nombre ?? ""}`.toLowerCase();
			const id = `${partida?.id ?? ""}`;
			const estado = `${partida?.estado ?? ""}`.toLowerCase();
			return nombre.includes(normalized) || id.includes(normalized) || estado.includes(normalized);
		});
	}, [partidas, search]);

	const emptyMessage = search.trim()
		? "No hay partidas que coincidan con la busqueda."
		: "No hay partidas.";

	return (
		<div className="app">
			<button className="partidas-volver-button" onClick={() => navigate("/inicio")}>⮜</button>
			<img src={cabecera} alt="Matacartas" style={{maxWidth: "100%", height: "auto"}} />
			<div className="partidas-toolbar-card">
				<input
					type="search"
					className="partidas-search-input"
					placeholder="Buscar partida..."
					aria-label="Buscar partida"
					disabled={loading}
				/>
				<button
					type="button"
					className="partidas-secondary-button"
					onClick={() => loadPartidas(page)}
					disabled={loading}
				>
					Actualizar
				</button>
			</div>
			{loading ? (
				<p style={{ fontWeight: "bold" }}>Cargando...</p>
			) : error ? (
				<p role="alert" style={{ fontWeight: "bold" }}>
					{error}
				</p>
			) : (
				<div className="partidas-table-wrap">
					<table className="partidas-table">
						<thead>
							<tr>
								<th>Nombre</th>
								<th>Jugadores</th>
								<th>Rango minimo</th>
								<th>Rango maximo</th>
								<th>Estado</th>
								<th> </th>
							</tr>
						</thead>
						<tbody>
							{filteredPartidas.length === 0 ? (
								<tr>
									<td colSpan={6}>{emptyMessage}</td>
								</tr>
							) : (
								filteredPartidas.map((partida, index) => {
									const rowKey = partida?.id ?? `${partida?.nombre ?? "partida"}-${index}`;
									const jugadoresActuales =
										typeof partida?.jugadores_actuales === "number"
											? partida.jugadores_actuales
											: partida?.jugadores_actuales ?? "";
									const jugadoresMaximos =
										typeof partida?.jugadores_maximos === "number"
											? partida.jugadores_maximos
											: partida?.jugadores_maximos ?? "";
									const jugadoresTexto =
										jugadoresActuales !== "" || jugadoresMaximos !== ""
											? `${jugadoresActuales}/${jugadoresMaximos}`
											: "";

									return (
										<tr key={rowKey}>
											<td>{partida?.nombre ?? ""}</td>
											<td>{jugadoresTexto}</td>
											<td>{partida?.rango_minimo ?? "-"}</td>
											<td>{partida?.rango_maximo ?? "-"}</td>
											<td>
												<span className={getEstadoClass(partida?.estado)}>
													{getEstadoLabel(partida?.estado)}
												</span>
											</td>
											<td>
												{partida?.estado === "sala_espera" ? (
													<button
														type="button"
														className="partidas-primary-button"
														onClick={() => navigate(`/partidas/${partida.id}`)}
														disabled={jugadoresActuales >= jugadoresMaximos}
													>
														Unirse
													</button>
												) : (
													<button
														type="button"
														className="partidas-primary-button"
														onClick={() => navigate(`/partidas/${partida.id}`)}
													>
														Ver
													</button>
												)}
											</td>
										</tr>
									);
								})
							)}
						</tbody>
					</table>
					<div className="partidas-pagination">
						<button
							type="button"
							className="partidas-secondary-button"
							onClick={() => setPage((prev) => Math.max(1, prev - 1))}
							disabled={loading || page <= 1}
						>
							Anterior
						</button>
						<span className="partidas-pagination__info">
							Pagina {page} de {totalPages} ({totalPartidas} partidas)
						</span>
						<button
							type="button"
							className="partidas-secondary-button"
							onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
							disabled={loading || page >= totalPages}
						>
							Siguiente
						</button>
					</div>
				</div>
			)}
		</div>
	);
}
