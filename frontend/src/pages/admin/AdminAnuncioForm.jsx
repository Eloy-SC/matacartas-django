import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../../styles/admin.css";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";

export default function AdminAnuncioForm() {
	const navigate = useNavigate();
	const { anuncioId } = useParams();
	const isEditMode = Boolean(anuncioId);
	const [form, setForm] = useState({ titulo: "", subtitulo: "", descripcion: "" });
	const [loading, setLoading] = useState(isEditMode);
	const [error, setError] = useState("");

	useEffect(() => {
		if (!anuncioId) {
			setLoading(false);
			return undefined;
		}

		let cancelled = false;
		fetch(`/api/anuncios/${anuncioId}/`, { credentials: "include" })
			.then(async (res) => {
				const data = await res.json().catch(() => ({}));
				if (!res.ok) throw new Error(data?.detail || "No se pudo cargar el anuncio");
				if (!cancelled) {
					setForm({ titulo: data?.titulo ?? "", subtitulo: data?.subtitulo ?? "", descripcion: data?.descripcion ?? "" });
				}
			})
			.catch((e) => {
				if (!cancelled) setError(e instanceof Error ? e.message : "Error cargando anuncio");
			})
			.finally(() => {
				if (!cancelled) setLoading(false);
			});
		return () => {
			cancelled = true;
		};
	}, [anuncioId]);

	async function handleSubmit(event) {
		event.preventDefault();
		setLoading(true);
		setError("");
		try {
			const csrfToken = await obtenerCsrfToken();
			const endpoint = isEditMode
				? `/api/anuncios/admin/${anuncioId}/editar/`
				: "/api/anuncios/admin/crear/";
			const res = await fetch(endpoint, {
				method: isEditMode ? "PUT" : "POST",
				credentials: "include",
				headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
				body: JSON.stringify(form),
			});
			const data = await res.json().catch(() => ({}));
			if (!res.ok) throw new Error(data?.detail || "No se pudo guardar el anuncio");
			navigate("/admin/anuncios");
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error guardando anuncio");
			setLoading(false);
		}
	}

	function updateField(event) {
		setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
	}

	return (
		<div className="app">
			<button className="admin-volver-button" onClick={() => navigate("/admin/anuncios/")}>⮜</button>
			<div className="admin-title-card">
				<h1 style={{ marginBottom: 0 }}>
					ADMINISTRACIÓN - ANUNCIOS
				</h1>
			</div>
			<div className="admin-form-card">
				{loading ? <p>Cargando...</p> : (
					<form onSubmit={handleSubmit}>
						<label htmlFor="titulo">Titulo *</label><br />
						<input id="titulo" name="titulo" value={form.titulo} onChange={updateField} required /><br />
						<label htmlFor="subtitulo">Subtitulo *</label><br />
						<input id="subtitulo" name="subtitulo" value={form.subtitulo} onChange={updateField} required /><br />
						<label htmlFor="descripcion">Descripcion *</label><br />
						<textarea id="descripcion" name="descripcion" value={form.descripcion} onChange={updateField} required rows={8} /><br />
						{error && <p role="alert">{error}</p>}
						<button type="submit" className="admin-primary-button" disabled={loading}>Guardar</button>
						<button type="button" className="admin-secondary-button" onClick={() => navigate("/admin/anuncios")} disabled={loading}>Volver</button>
					</form>
				)}
				{error && !form.titulo && <p role="alert">{error}</p>}
			</div>
		</div>
	);
}
