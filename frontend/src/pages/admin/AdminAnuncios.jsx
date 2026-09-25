import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/admin.css";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";

function formatDate(value) {
	if (!value) return "-";

	const date = new Date(value);
	return Number.isNaN(date.getTime()) ? value : date.toLocaleString("es-ES");
}

export default function AdminAnuncios() {
	const navigate = useNavigate();
	const [anuncios, setAnuncios] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [deletingId, setDeletingId] = useState(null);
    const [publicandoId, setPublicandoId] = useState(null);

	const loadAnuncios = useCallback(() => {
		let cancelled = false;
		setLoading(true);
		setError("");

		fetch("/api/anuncios/admin/listar/", { method: "GET", credentials: "include" })
			.then(async (res) => {
				const data = await res.json().catch(() => []);
				if (cancelled) return;
				if (!res.ok) {
					throw new Error(data?.detail || "No se pudo cargar la lista de anuncios");
				}
				setAnuncios(Array.isArray(data) ? data : []);
			})
			.catch((e) => {
				if (cancelled) return;
				setError(e instanceof Error ? e.message : "Error cargando anuncios");
				setAnuncios([]);
			})
			.finally(() => {
				if (!cancelled) setLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, []);

	useEffect(() => {
		const cancel = loadAnuncios();
		return () => {
			if (typeof cancel === "function") cancel();
		};
	}, [loadAnuncios]);

	async function handlePublicar(anuncioId) {
		if (!anuncioId || publicandoId) return;
		if (!window.confirm("¿Seguro que quieres publicar este anuncio?")) return;

		setPublicandoId(anuncioId);
		setError("");
		try {
			const csrfToken = await obtenerCsrfToken();
			const res = await fetch(`/api/anuncios/admin/${anuncioId}/publicar/`, {
				method: "PUT",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
			});
			const data = await res.json().catch(() => ({}));
			if (!res.ok) throw new Error(data?.detail || "No se pudo publicar el anuncio");
			loadAnuncios();
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error publicando anuncio");
		} finally {
			setPublicandoId(null);
		}
	}

	async function handleDelete(anuncioId) {
		if (!anuncioId || deletingId) return;
		if (!window.confirm("¿Seguro que quieres eliminar este anuncio?")) return;

		setDeletingId(anuncioId);
		setError("");
		try {
			const csrfToken = await obtenerCsrfToken();
			const res = await fetch(`/api/anuncios/admin/${anuncioId}/eliminar/`, {
				method: "DELETE",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
			});
			const data = await res.json().catch(() => ({}));
			if (!res.ok) throw new Error(data?.detail || "No se pudo eliminar el anuncio");
			loadAnuncios();
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error eliminando anuncio");
		} finally {
			setDeletingId(null);
		}
	}

	return (
		<div className="app">
			<button className="admin-volver-button" onClick={() => navigate("/admin")}>⮜</button>
			<div className="admin-title-card">
				<h1 style={{ marginBottom: 0 }}>ADMINISTRACION - ANUNCIOS</h1>
			</div>
            <button
                type="button"
                className="admin-primary-button"
                style={{ marginBottom: "1rem" }}
                onClick={() => navigate("/admin/anuncios/crear")}
                disabled={loading}
            >
                Crear anuncio
            </button>
			{loading ? (
				<p style={{ fontWeight: "bold", color: "white" }}>Cargando...</p>
			) : error ? (
				<p role="alert" style={{ fontWeight: "bold", color: "white" }}>{error}</p>
			) : (
				<div className="admin-users-table-wrap">
					<table className="admin-users-table">
						<thead>
							<tr>
								<th>Titulo</th>
								<th>Ultima modificacion</th>
                                <th>Autor</th>
								<th>Publico</th>
								<th>Fecha de publicacion</th>
								<th>Acciones</th>
							</tr>
						</thead>
						<tbody>
							{anuncios.length === 0 ? (
								<tr><td colSpan={6}>No hay anuncios.</td></tr>
							) : anuncios.map((anuncio) => (
								<tr key={anuncio.id}>
									<td>{anuncio.titulo ?? ""}</td>
									<td>{formatDate(anuncio.fecha_ult_mod)}</td>
                                    <td>{anuncio.autor ?? "Autor desconocido"}</td>
									<td>{anuncio.fecha_publicacion ? "Si" : "No"}</td>
									<td>{formatDate(anuncio.fecha_publicacion)}</td>
									<td>
										<div className="admin-actions">
											<button type="button" className="admin-icon-button" aria-label="Editar anuncio" onClick={() => navigate(`/admin/anuncios/${anuncio.id}`)} disabled={deletingId === anuncio.id || publicandoId === anuncio.id || anuncio.fecha_publicacion}>
												<svg viewBox="0 0 24 24" role="img" aria-hidden="true" className="admin-icon"><path d="M3 17.25V21h3.75L19.81 7.94l-3.75-3.75L3 17.25zm2.92 2.33H5v-.92l9.06-9.06.92.92L5.92 19.58zM20.71 6.04a1 1 0 0 0 0-1.41L19.37 3.3a1 1 0 0 0-1.41 0l-1.09 1.09 3.75 3.75 1.09-1.1z" /></svg>
											</button>
											<button type="button" className="admin-delete-button" aria-label="Borrar anuncio" onClick={() => handleDelete(anuncio.id)} disabled={deletingId === anuncio.id || publicandoId === anuncio.id}>
												<svg viewBox="0 0 24 24" role="img" aria-hidden="true" className="admin-icon"><path d="M9 3h6l1 1h4v2H4V4h4l1-1zm1 6h2v9h-2V9zm4 0h2v9h-2V9zM7 9h2v9H7V9zm-1 12h12a1 1 0 0 1-1-1V8H5v12a1 1 0 0 1 1 1z" /></svg>
											</button>
                                            <button type="button" className="admin-delete-button" aria-label="Publicar anuncio" onClick={() => handlePublicar(anuncio.id)} disabled={deletingId === anuncio.id || publicandoId === anuncio.id}>
												Publicar
											</button>
										</div>
									</td>
								</tr>
							))}
						</tbody>
					</table>
				</div>
			)}
		</div>
	);
}
