
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/admin.css";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";

const CATEGORIA_LABELS = {
	oro: "ORO",
	plata: "PLATA",
	bronce: "BRONCE",
};

export default function AdminMedallas() {
	const navigate = useNavigate();
	const [medallas, setMedallas] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [deletingId, setDeletingId] = useState(null);
	const [search, setSearch] = useState("");

	const loadMedallas = useCallback(() => {
		let cancelled = false;
		setLoading(true);
		setError("");

		fetch("/api/medallas/listar/", { method: "GET", credentials: "include" })
			.then(async (res) => {
				const data = await res.json().catch(() => []);
				if (cancelled) return;
				if (!res.ok) {
					const detail = data?.detail || "No se pudo cargar la lista de medallas";
					throw new Error(detail);
				}
				setMedallas(Array.isArray(data) ? data : []);
			})
			.catch((e) => {
				if (cancelled) return;
				setError(e instanceof Error ? e.message : "Error cargando medallas");
				setMedallas([]);
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
		const cancel = loadMedallas();
		return () => {
			if (typeof cancel === "function") cancel();
		};
	}, [loadMedallas]);

	async function handleDelete(medallaId) {
		if (!medallaId || deletingId) return;
		const ok = window.confirm("¿Seguro que quieres eliminar esta medalla?");
		if (!ok) return;

		setDeletingId(medallaId);
		setError("");
		try {
			const csrfToken = await obtenerCsrfToken();

			const res = await fetch(`/api/medallas/admin/${medallaId}/eliminar/`, {
				method: "DELETE",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
			});
			const data = await res.json().catch(() => ({}));
			if (!res.ok) {
				throw new Error(data?.detail || "No se pudo eliminar la medalla");
			}

			loadMedallas();
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error eliminando medalla");
		} finally {
			setDeletingId(null);
		}
	}

	const filteredMedallas = useMemo(() => {
		const term = search.trim().toLowerCase();
		if (!term) return medallas;
		return medallas.filter((medalla) => {
			const nombre = (medalla?.nombre ?? "").toLowerCase();
			const categoria = (medalla?.categoria ?? "").toLowerCase();
			return nombre.includes(term) || categoria.includes(term);
		});
	}, [medallas, search]);

	return (
		<div className="app">
			<button className="admin-volver-button" onClick={() => navigate("/admin/recompensas")}>
				⮜
			</button>
			<div className="admin-title-card">
				<h1 style={{ marginBottom: 0 }}>ADMINISTRACION - MEDALLAS</h1>
			</div>
			<div className="admin-toolbar-card">
				<input
					type="search"
					className="admin-search-input"
					placeholder="Buscar medalla..."
					aria-label="Buscar medalla"
					value={search}
					onChange={(e) => setSearch(e.target.value)}
					disabled={loading}
				/>
				<button
					type="button"
					className="admin-primary-button"
					onClick={() => navigate("/admin/recompensas/medallas/crear")}
					disabled={loading}
				>
					Crear medalla
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
								<th>Categoria</th>
								<th>Imagen</th>
								<th>Acciones</th>
							</tr>
						</thead>
						<tbody>
							{filteredMedallas.length === 0 ? (
								<tr>
									<td colSpan={4}>No hay medallas.</td>
								</tr>
							) : (
								filteredMedallas.map((medalla) => (
									<tr key={medalla.id ?? medalla.nombre}>
										<td>{medalla.nombre ?? ""}</td>
										<td>{CATEGORIA_LABELS[medalla.categoria] ?? medalla.categoria ?? ""}</td>
										<td>
											{medalla.imagen ? (
												<img
													src={medalla.imagen}
													alt={`Imagen de ${medalla.nombre ?? "medalla"}`}
													style={{ width: 48, height: 48, objectFit: "cover", borderRadius: 6 }}
													onError={(e) => {
														e.currentTarget.style.display = "none";
													}}
												/>
											) : (
												"-"
											)}
										</td>
										<td>
											<div className="admin-actions">
												<button
													type="button"
													className="admin-icon-button"
													aria-label="Editar medalla"
													onClick={() => navigate(`/admin/recompensas/medallas/${medalla.id}`)}
													disabled={loading || deletingId === medalla.id}
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
													aria-label="Borrar medalla"
													onClick={() => handleDelete(medalla.id)}
													disabled={loading || deletingId === medalla.id}
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