import { useCallback, useEffect, useState } from "react";
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

const ORDER_FIELDS = [
	{ value: "nombre", label: "Nombre" },
	{ value: "num_jugadores", label: "Jugadores maximos" },
	{ value: "rango_minimo_id", label: "Rango minimo" },
	{ value: "rango_maximo_id", label: "Rango maximo" },
	{ value: "fecha_creacion", label: "Fecha de creacion" },
];

function getEstadoLabel(estado) {
	if (!estado) return ESTADO_LABELS.desconocido;
	return ESTADO_LABELS[estado] ?? ESTADO_LABELS.desconocido;
}

function getEstadoClass(estado) {
	if (!estado) return ESTADO_CLASS.desconocido;
	return ESTADO_CLASS[estado] ?? ESTADO_CLASS.desconocido;
}

function formatFecha(value) {
	if (!value) return "-";
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return `${value}`;
	return date.toLocaleString();
}

export default function ListaPartidas() {
	const navigate = useNavigate();
	const [partidas, setPartidas] = useState([]);
	const [rangos, setRangos] = useState([]);
	const [page, setPage] = useState(1);
	const [totalPages, setTotalPages] = useState(1);
	const [totalPartidas, setTotalPartidas] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [search, setSearch] = useState("");
	const [debouncedSearch, setDebouncedSearch] = useState("");
	const [selectedNumJugadores, setSelectedNumJugadores] = useState("");
	const [selectedRangoMin, setSelectedRangoMin] = useState("");
	const [selectedRangoMax, setSelectedRangoMax] = useState("");
	const [orderBy, setOrderBy] = useState("id");
	const [orderDir, setOrderDir] = useState("asc");
	const [clave, setClave] = useState("");
	const [joiningPartidaId, setJoiningPartidaId] = useState(null);

	const handleUnirse = async (id, key, privada) => {
		const partidaKey = privada ? key : id;
		if (partidaKey === undefined || partidaKey === null || partidaKey === "") {
			alert("Falta el identificador de la partida");
			return;
		}

		if (joiningPartidaId) return; // Prevenir múltiples clics

		setJoiningPartidaId(partidaKey);

		try {
			const participaRes = await fetch(
				privada ? `/api/partidas/${partidaKey}/participa/` : `/api/partidas/${partidaKey}/participa/`,
				{
					method: "GET",
					credentials: "include",
				}
			);

			if (!participaRes.ok) {
				throw new Error("No se pudo verificar la participación");
			}

			const participaData = await participaRes.json().catch(() => ({}));
			const partidaIdDestino = participaData?.id ?? id ?? partidaKey;

			if (participaData?.participa) {
				navigate(`/partidas/sala-de-espera/${partidaIdDestino}`);
				return;
			}

			const csrfRes = await fetch("/api/auth/csrf/", {
				method: "GET",
				credentials: "include",
			});

			if (!csrfRes.ok) {
				throw new Error("No se pudo obtener el token CSRF");
			}

			const { csrfToken } = await csrfRes.json().catch(() => ({}));
			if (!csrfToken) {
				throw new Error("Token CSRF no disponible");
			}

			const unirseRes = await fetch(
				privada ? `/api/partidas/${partidaKey}/unirse/` : `/api/partidas/${partidaKey}/unirse/`,
				{
					method: "POST",
					credentials: "include",
					headers: {
						"Content-Type": "application/json",
						"X-CSRFToken": csrfToken,
					},
				}
			);

			if (!unirseRes.ok) {
				const unirseData = await unirseRes.json().catch(() => ({}));
				throw new Error(unirseData?.detail || "No se pudo unir a la partida");
			}

			navigate(`/partidas/sala-de-espera/${partidaIdDestino}`);
		} catch (e) {
			alert(e instanceof Error ? e.message : "Error al procesar la unión");
		} finally {
			setJoiningPartidaId(null);
		}
	};

	const loadRangos = useCallback(() => {
		let cancelled = false;

		fetch("/api/rangos/listar/", {
			method: "GET",
			credentials: "include",
		})
			.then(async (res) => {
				const data = await res.json().catch(() => []);
				if (cancelled) return;
				if (!res.ok) {
					throw new Error(data?.detail || "No se pudo cargar la lista de rangos");
				}
				setRangos(Array.isArray(data) ? data : []);
			})
			.catch(() => {
				if (cancelled) return;
				setRangos([]);
			});

		return () => {
			cancelled = true;
		};
	}, []);

	const loadPartidas = useCallback((pageNumber = 1) => {
		let cancelled = false;
		setLoading(true);
		setError("");

		const params = new URLSearchParams();
		params.set("page", String(pageNumber));
		if (debouncedSearch.trim()) {
			params.set("search", debouncedSearch.trim());
		}
		if (selectedNumJugadores) {
			params.set("num_jugadores", selectedNumJugadores);
		}
		if (selectedRangoMin) {
			params.set("rango_minimo_id", selectedRangoMin);
		}
		if (selectedRangoMax) {
			params.set("rango_maximo_id", selectedRangoMax);
		}
		if (orderBy) {
			const orderingValue = orderDir === "desc" ? `-${orderBy}` : orderBy;
			params.set("ordering", orderingValue);
		}

		fetch(`/api/partidas/publicas/?${params.toString()}`, {
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
	}, [debouncedSearch, selectedNumJugadores, selectedRangoMin, selectedRangoMax, orderBy, orderDir]);

	useEffect(() => {
		const cancel = loadRangos();
		return () => {
			if (typeof cancel === "function") cancel();
		};
	}, [loadRangos]);

	useEffect(() => {
		const cancel = loadPartidas(page);
		return () => {
			if (typeof cancel === "function") cancel();
		};
	}, [loadPartidas, page]);

	useEffect(() => {
		const timeoutId = setTimeout(() => {
			setDebouncedSearch(search);
		}, 300);
		return () => {
			clearTimeout(timeoutId);
		};
	}, [search]);

	useEffect(() => {
		setPage(1);
	}, [debouncedSearch, selectedNumJugadores, selectedRangoMin, selectedRangoMax, orderBy, orderDir]);

	const emptyMessage = debouncedSearch.trim()
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
					value={search}
					onChange={(e) => setSearch(e.target.value)}
					disabled={loading}
				/>
				<select
					className="partidas-search-input"
					value={selectedNumJugadores}
					onChange={(e) => setSelectedNumJugadores(e.target.value)}
					aria-label="Filtrar por jugadores"
					disabled={loading}
				>
					<option value="">Todos los jugadores</option>
					{[2, 3, 4, 5, 6].map((value) => (
						<option key={value} value={String(value)}>
							{value} jugadores
						</option>
					))}
				</select>
				<select
					className="partidas-search-input"
					value={selectedRangoMin}
					onChange={(e) => setSelectedRangoMin(e.target.value)}
					aria-label="Filtrar por rango minimo"
					disabled={loading}
				>
					<option value="">Rango minimo</option>
					{rangos.map((rango) => (
						<option key={rango.id ?? rango.nombre} value={rango.id ?? ""}>
							{rango.nombre ?? ""}
						</option>
					))}
				</select>
				<select
					className="partidas-search-input"
					value={selectedRangoMax}
					onChange={(e) => setSelectedRangoMax(e.target.value)}
					aria-label="Filtrar por rango maximo"
					disabled={loading}
				>
					<option value="">Rango maximo</option>
					{rangos.map((rango) => (
						<option key={rango.id ?? rango.nombre} value={rango.id ?? ""}>
							{rango.nombre ?? ""}
						</option>
					))}
				</select>
				<input
					className="partidas-search-input"
					placeholder="Introduce la clave de la partida"
					aria-label="Clave de partida privada"
					disabled={loading}
					value={clave}
					onChange={(e) => setClave(e.target.value)}
				/>
				<button
					type="button"
					className="partidas-secondary-button"
					onClick={() => handleUnirse(undefined, clave, true)}
					disabled={loading || joiningPartidaId === clave}
				>
					{joiningPartidaId === clave ? "Uniéndose..." : "Unirse a partida privada"}
				</button>
				<select
					className="partidas-search-input"
					value={orderBy}
					onChange={(e) => setOrderBy(e.target.value)}
					aria-label="Ordenar por"
					disabled={loading}
				>
					{ORDER_FIELDS.map((field) => (
						<option key={field.value} value={field.value}>
							Ordenar: {field.label}
						</option>
					))}
				</select>
				<select
					className="partidas-search-input"
					value={orderDir}
					onChange={(e) => setOrderDir(e.target.value)}
					aria-label="Ordenar direccion"
					disabled={loading}
				>
					<option value="asc">Ascendente</option>
					<option value="desc">Descendente</option>
				</select>
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
								<th>Rango mínimo</th>
								<th>Rango máximo</th>
								<th>Fecha de creación</th>
								<th>Estado</th>
								<th> </th>
							</tr>
						</thead>
						<tbody>
							{partidas.length === 0 ? (
								<tr>
									<td colSpan={7}>{emptyMessage}</td>
								</tr>
							) : (
								partidas.map((partida, index) => {
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
									const fechaCreacion = formatFecha(partida?.fecha_creacion);

									return (
										<tr key={rowKey}>
											<td>{partida?.nombre ?? ""}</td>
											<td>{jugadoresTexto}</td>
											<td>{partida?.rango_minimo ?? "-"}</td>
											<td>{partida?.rango_maximo ?? "-"}</td>
											<td>{fechaCreacion}</td>
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
														onClick={() => handleUnirse(partida.id, undefined, false)}
														disabled={jugadoresActuales >= jugadoresMaximos || joiningPartidaId === partida.id}
													>
														{joiningPartidaId === partida.id ? "Uniéndose..." : "Unirse"}
													</button>
												) : (
													<button
														type="button"
														className="partidas-primary-button"
														/*onClick={() => navigate(`/partidas/sala-de-espera/${partida.id}`)}*/
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
