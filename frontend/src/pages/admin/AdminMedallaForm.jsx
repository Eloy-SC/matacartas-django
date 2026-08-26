import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";
import "../../styles/admin.css";

const CATEGORIA_OPTIONS = [
	{ value: "oro", label: "ORO" },
	{ value: "plata", label: "PLATA" },
	{ value: "bronce", label: "BRONCE" },
];

export default function AdminMedallaForm() {
	const navigate = useNavigate();
	const { medallaId } = useParams();
	const mode = useMemo(() => (medallaId ? "edit" : "create"), [medallaId]);

	const [nombre, setNombre] = useState("");
	const [categoria, setCategoria] = useState("bronce");
	const [imagen, setImagen] = useState("");
	const [imgPreviewError, setImgPreviewError] = useState(false);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [successMessage, setSuccessMessage] = useState("");

	useEffect(() => {
		let cancelled = false;
		setError("");
		setSuccessMessage("");
		setImgPreviewError(false);

		if (!medallaId) return () => {};

		setLoading(true);
		fetch(`/api/medallas/${medallaId}/`, { method: "GET", credentials: "include" })
			.then(async (res) => {
				const data = await res.json().catch(() => ({}));
				if (cancelled) return;
				if (!res.ok) {
					throw new Error(data?.detail || "No se pudo cargar la medalla");
				}
				setNombre(data?.nombre ?? "");
				setCategoria(data?.categoria ?? "bronce");
				setImagen(data?.imagen ?? "");
			})
			.catch((e) => {
				if (cancelled) return;
				setError(e instanceof Error ? e.message : "Error cargando medalla");
			})
			.finally(() => {
				if (cancelled) return;
				setLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, [medallaId]);

	async function handleSubmit(event) {
		event.preventDefault();
		setError("");
		setSuccessMessage("");

		if (!nombre || !categoria) {
			setError("Introduce todos los campos requeridos");
			return;
		}

		setLoading(true);
		try {
			const csrfToken = await obtenerCsrfToken();

			const payload = {
				nombre: nombre.trim(),
				categoria,
				imagen: imagen.trim() || null,
			};

			const endpoint = medallaId
				? `/api/medallas/admin/${medallaId}/editar/`
				: "/api/medallas/admin/crear/";
			const method = medallaId ? "PUT" : "POST";
			const res = await fetch(endpoint, {
				method,
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
				body: JSON.stringify(payload),
			});

			const data = await res.json().catch(() => ({}));
			if (!res.ok) {
				const detail = data?.detail || "No se pudo guardar la medalla";
				throw new Error(detail);
			}

			setSuccessMessage(medallaId ? "Medalla actualizada" : "Medalla creada");
			navigate("/admin/recompensas/medallas");
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error guardando medalla");
		} finally {
			setLoading(false);
		}
	}

	const showImagePreview = Boolean(imagen) && !imgPreviewError;

	return (
		<div className="app">
			<div className="admin-title-card">
				<h1 style={{ marginBottom: 0 }}>
					{mode === "edit" ? "ADMINISTRACION - EDITAR MEDALLA" : "ADMINISTRACION - CREAR MEDALLA"}
				</h1>
			</div>
			<div className="admin-form-card">
				<form onSubmit={handleSubmit}>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="nombre">Nombre *</label>
						<br />
						<input
							id="nombre"
							name="nombre"
							value={nombre}
							onChange={(e) => setNombre(e.target.value)}
							disabled={loading}
						/>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="categoria">Categoria *</label>
						<br />
						<select
							id="categoria"
							name="categoria"
							value={categoria}
							onChange={(e) => setCategoria(e.target.value)}
							disabled={loading}
						>
							{CATEGORIA_OPTIONS.map((option) => (
								<option key={option.value} value={option.value}>
									{option.label}
								</option>
							))}
						</select>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="imagen">Imagen (URL)</label>
						<br />
						<input
							id="imagen"
							name="imagen"
							type="url"
							placeholder="https://..."
							value={imagen}
							onChange={(e) => {
								setImagen(e.target.value);
								setImgPreviewError(false);
							}}
							disabled={loading}
						/>
						{showImagePreview && (
							<div style={{ marginTop: 8 }}>
								<img
									src={imagen}
									alt="Previsualizacion de medalla"
									style={{ width: 80, height: 80, objectFit: "cover", borderRadius: 8 }}
									onError={() => setImgPreviewError(true)}
								/>
							</div>
						)}
					</div>
					<div style={{ marginTop: 12 }}>
						<button type="submit" className="admin-primary-button">
							{mode === "edit" ? "Guardar cambios" : "Crear medalla"}
						</button>
						<button
							type="button"
							className="admin-secondary-button"
							onClick={() => navigate("/admin/recompensas/medallas")}
							style={{ marginLeft: 8 }}
							disabled={loading}
						>
							Volver
						</button>
					</div>
					{error && (
						<p role="alert" style={{ marginTop: 12, whiteSpace: "pre-line", color: "red", fontWeight: "bold" }}>
							{error}
						</p>
					)}
					{successMessage && (
						<p style={{ marginTop: 12, color: "green", fontWeight: "bold" }}>{successMessage}</p>
					)}
				</form>
			</div>
		</div>
	);
}
