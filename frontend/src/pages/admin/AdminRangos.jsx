import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/admin.css";
import "../../styles/rangos.css";

const COLOR_LABELS = {
	blanco: "BLANCO",
	negro: "NEGRO",
	rosa: "ROSA",
	rosa_fuxia: "ROSA FUXIA",
	rojo_claro: "ROJO CLARO",
	rojo: "ROJO",
	rojo_oscuro: "ROJO OSCURO",
	verde_claro: "VERDE CLARO",
	verde_esperanza: "VERDE ESPERANZA",
	verde: "VERDE",
	verde_oscuro: "VERDE OSCURO",
	azul_claro: "AZUL CLARO",
	azul: "AZUL",
	azul_oscuro: "AZUL OSCURO",
	azul_cian: "AZUL CIAN",
	amarillo: "AMARILLO",
	amarillo_dorado: "DORADO",
	amarillo_naranja: "AMARILLO ANARANJADO",
	naranja: "NARANJA",
	morado_claro: "MORADO CLARO",
	morado: "MORADO",
	morado_oscuro: "MORADO OSCURO",
	gris: "GRIS",
	gris_plata: "PLATA",
	marron_bronce: "BRONCE",
	marron: "MARRON",
};

export default function AdminRangos() {
	const navigate = useNavigate();
	const [rangos, setRangos] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [deletingId, setDeletingId] = useState(null);
	const [search, setSearch] = useState("");

	const loadRangos = useCallback(() => {
		let cancelled = false;
		setLoading(true);
		setError("");

		fetch("/api/rangos/listar/", { method: "GET", credentials: "include" })
			.then(async (res) => {
				const data = await res.json().catch(() => []);
				if (cancelled) return;
				if (!res.ok) {
					const detail = data?.detail || "No se pudo cargar la lista de rangos";
					throw new Error(detail);
				}
				setRangos(Array.isArray(data) ? data : []);
			})
			.catch((e) => {
				if (cancelled) return;
				setError(e instanceof Error ? e.message : "Error cargando rangos");
				setRangos([]);
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
		const cancel = loadRangos();
		return () => {
			if (typeof cancel === "function") cancel();
		};
	}, [loadRangos]);

	async function handleDelete(rangoId) {
		if (!rangoId || deletingId) return;
		const ok = window.confirm("¿Seguro que quieres eliminar este rango?");
		if (!ok) return;

		setDeletingId(rangoId);
		setError("");
		try {
			const csrfRes = await fetch("/api/auth/csrf/", {
				method: "GET",
				credentials: "include",
			});
			if (!csrfRes.ok) {
				throw new Error("No se pudo obtener el token CSRF");
			}
			const { csrfToken } = await csrfRes.json();

			const res = await fetch(`/api/rangos/admin/${rangoId}/eliminar/`, {
				method: "DELETE",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
			});
			const data = await res.json().catch(() => ({}));
			if (!res.ok) {
				throw new Error(data?.detail || "No se pudo eliminar el rango");
			}

			loadRangos();
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error eliminando rango");
		} finally {
			setDeletingId(null);
		}
	}

	const filteredRangos = useMemo(() => {
		const term = search.trim().toLowerCase();
		if (!term) return rangos;
		return rangos.filter((rango) => (rango?.nombre ?? "").toLowerCase().includes(term));
	}, [rangos, search]);

	return (
		<div className="app">
			<button className="admin-volver-button" onClick={() => navigate("/admin")}>⮜</button>
			<div className="admin-title-card">
				<h1 style={{ marginBottom: 0 }}>ADMINISTRACION - RANGOS</h1>
			</div>
			<div className="admin-toolbar-card">
				<input
					type="search"
					className="admin-search-input"
					placeholder="Buscar rango..."
					aria-label="Buscar rango"
					value={search}
					onChange={(e) => setSearch(e.target.value)}
					disabled={loading}
				/>
				<button
					type="button"
					className="admin-primary-button"
					onClick={() => navigate("/admin/rangos/crear")}
					disabled={loading}
				>
					Crear rango
				</button>
			</div>
			{loading ? (
				<p style={{ fontWeight: "bold", color: "white" }}>Cargando...</p>
			) : error ? (
				<p role="alert" style={{ fontWeight: "bold", color: "white" }}>
					{error}
				</p>
			) : (
				<div className="admin-users-table-wrap">
					<table className="admin-users-table">
						<thead>
							<tr>
								<th>Nombre</th>
								<th>Puntuacion minima</th>
								<th>Puntuacion maxima</th>
								<th>Acciones</th>
							</tr>
						</thead>
						<tbody>
							{filteredRangos.length === 0 ? (
								<tr>
									<td colSpan={4}>No hay rangos.</td>
								</tr>
							) : (
								filteredRangos.map((rango) => (
									<tr key={rango.id ?? rango.nombre}>
										<td>
											<span
												className={`rango-text rango-color-${(rango.color ?? "")
													.replace(/_/g, "-")
													.toLowerCase()}`}
											>
												{rango.nombre ?? ""}
											</span>
										</td>
										<td>{rango.puntos_minimos ?? ""}</td>
										<td>{rango.puntos_maximos ?? ""}</td>
										<td>
											<div className="admin-actions">
												<button
													type="button"
													className="admin-icon-button"
													aria-label="Editar rango"
													onClick={() => navigate(`/admin/rangos/${rango.id}`)}
													disabled={loading || deletingId === rango.id}
												>
													<svg
														viewBox="0 0 24 24"
														role="img"
														aria-hidden="true"
														className="admin-icon"
													>
														<path d="M3 17.25V21h3.75L19.81 7.94l-3.75-3.75L3 17.25zm2.92 2.33H5v-.92l9.06-9.06.92.92L5.92 19.58zM20.71 6.04a1 1 0 0 0 0-1.41L19.37 3.3a1 1 0 0 0-1.41 0l-1.09 1.09 3.75 3.75 1.09-1.1z" />
													</svg>
												</button>
												<button
													type="button"
													className="admin-delete-button"
													aria-label="Borrar rango"
													onClick={() => handleDelete(rango.id)}
													disabled={loading || deletingId === rango.id}
												>
													<svg
														viewBox="0 0 24 24"
														role="img"
														aria-hidden="true"
														className="admin-icon"
													>
														<path d="M9 3h6l1 1h4v2H4V4h4l1-1zm1 6h2v9h-2V9zm4 0h2v9h-2V9zM7 9h2v9H7V9zm-1 12h12a1 1 0 0 0 1-1V8H5v12a1 1 0 0 0 1 1z" />
													</svg>
												</button>
											</div>
										</td>
									</tr>
								))
							)}
						</tbody>
					</table>
				</div>
			)}
		</div>
	);
}
