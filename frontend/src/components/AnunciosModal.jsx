import { useEffect, useState } from "react";

function formatDate(value) {
	if (!value) return "-";
	const date = new Date(value);
	return Number.isNaN(date.getTime()) ? value : date.toLocaleString("es-ES");
}

export default function AnunciosModal({ onClose }) {
	const [anuncios, setAnuncios] = useState([]);
	const [selectedAnuncio, setSelectedAnuncio] = useState(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	async function loadAnuncios() {
		setLoading(true);
		setError("");
		try {
			const response = await fetch("/api/anuncios/publicos/listar/", {
				method: "GET",
				credentials: "include",
			});
			const data = await response.json().catch(() => []);
			if (!response.ok) throw new Error(data?.detail || "No se pudieron cargar los anuncios");
			setAnuncios(Array.isArray(data) ? data : []);
		} catch (exception) {
			setError(exception instanceof Error ? exception.message : "Error cargando anuncios");
			setAnuncios([]);
		} finally {
			setLoading(false);
		}
	}

	useEffect(() => {
		loadAnuncios();
	}, []);

	async function handleSelect(anuncio) {
		setLoading(true);
		setError("");
		try {
			const response = await fetch(`/api/anuncios/${anuncio.id}/`, {
				method: "GET",
				credentials: "include",
			});
			const data = await response.json().catch(() => ({}));
			if (!response.ok) throw new Error(data?.detail || "No se pudo cargar el anuncio");
			setSelectedAnuncio(data);
		} catch (exception) {
			setError(exception instanceof Error ? exception.message : "Error cargando anuncio");
		} finally {
			setLoading(false);
		}
	}

	async function handleBack() {
		setSelectedAnuncio(null);
		await loadAnuncios();
	}

	return (
		<div
			className="form-card"
			role="dialog"
			aria-modal="true"
			aria-labelledby="anuncios-modal-title"
			style={{
				position: "fixed",
				top: "50%",
				left: "50%",
				transform: "translate(-50%, -50%)",
				zIndex: 10,
				width: "min(680px, calc(100% - 32px))",
				maxHeight: "80vh",
				overflow: "hidden",
			}}
		>
			<button type="button" onClick={onClose} aria-label="Cerrar" className="close-card-button">X</button>
			{selectedAnuncio && (
				<button
					type="button"
					onClick={handleBack}
					aria-label="Volver a la lista de anuncios"
					style={{ padding: "4px 10px", marginBottom: 12 }}
				>
					←
				</button>
			)}
			<h2 id="anuncios-modal-title" style={{marginBottom: 15}}>{selectedAnuncio ? selectedAnuncio.titulo : "Anuncios"}</h2>
			{loading ? (
				<p style={{ fontWeight: "bold" }}>Cargando...</p>
			) : error ? (
				<p role="alert">{error}</p>
			) : selectedAnuncio ? (
				<div style={{ overflowY: "auto", maxHeight: "55vh", paddingRight: 8 }}>
					<p style={{ color: "black" }}><strong>{selectedAnuncio.subtitulo}</strong></p>
					<p style={{ color: "black", textAlign: "justify" }}>{selectedAnuncio.descripcion}</p>
					<p style={{ color: "black" }}><strong>Publicado el </strong> {formatDate(selectedAnuncio.fecha_publicacion)}</p>
					<p style={{ color: "black" }}><strong>Autor:</strong> {selectedAnuncio.autor}</p>
				</div>
			) : (
				<div style={{ overflowY: "auto", maxHeight: "55vh", display: "grid", gap: 8, paddingRight: 8 }}>
					{anuncios.length === 0 ? (
						<p>No hay anuncios publicados.</p>
					) : anuncios.map((anuncio) => (
						<button
							key={anuncio.id}
							type="button"
							onClick={() => handleSelect(anuncio)}
							style={{ textAlign: "left", width: "100%" }}
						>
							<strong>{anuncio.titulo}</strong>
							<br />
							<span>{anuncio.subtitulo}</span>
							<br />
							<small>{formatDate(anuncio.fecha_publicacion)}</small>
						</button>
					))}
				</div>
			)}
		</div>
	);
}
