import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../../styles/admin.css";
import "../../styles/rangos.css";

const COLOR_OPTIONS = [
	{ value: "blanco", label: "BLANCO" },
	{ value: "negro", label: "NEGRO" },
	{ value: "rosa", label: "ROSA" },
	{ value: "rojo_claro", label: "ROJO CLARO" },
	{ value: "rojo", label: "ROJO" },
	{ value: "rojo_oscuro", label: "ROJO OSCURO" },
	{ value: "verde_claro", label: "VERDE CLARO" },
	{ value: "verde_esperanza", label: "VERDE ESPERANZA" },
	{ value: "verde", label: "VERDE" },
	{ value: "verde_oscuro", label: "VERDE OSCURO" },
	{ value: "azul_claro", label: "AZUL CLARO" },
	{ value: "azul", label: "AZUL" },
	{ value: "azul_oscuro", label: "AZUL OSCURO" },
	{ value: "azul_cian", label: "AZUL CIAN" },
	{ value: "amarillo", label: "AMARILLO" },
	{ value: "amarillo_dorado", label: "DORADO" },
	{ value: "amarillo_naranja", label: "AMARILLO ANARANJADO" },
	{ value: "naranja", label: "NARANJA" },
	{ value: "morado_claro", label: "PÚRPURA" },
	{ value: "morado", label: "MORADO" },
	{ value: "morado_oscuro", label: "MORADO OSCURO" },
	{ value: "gris", label: "GRIS" },
	{ value: "gris_plata", label: "PLATA" },
	{ value: "marron_bronce", label: "BRONCE" },
	{ value: "marron", label: "MARRON" },
];

export default function AdminRangoForm() {
	const navigate = useNavigate();
	const { rangoId } = useParams();
	const mode = useMemo(() => (rangoId ? "edit" : "create"), [rangoId]);

	const [nombre, setNombre] = useState("");
	const [puntosMinimos, setPuntosMinimos] = useState("");
	const [puntosMaximos, setPuntosMaximos] = useState("");
	const [color, setColor] = useState("verde");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [successMessage, setSuccessMessage] = useState("");

	useEffect(() => {
		let cancelled = false;
		setError("");
		setSuccessMessage("");

		if (!rangoId) return () => {};

		setLoading(true);
		fetch(`/api/rangos/${rangoId}/`, { method: "GET", credentials: "include" })
			.then(async (res) => {
				const data = await res.json().catch(() => ({}));
				if (cancelled) return;
				if (!res.ok) {
					throw new Error(data?.detail || "No se pudo cargar el rango");
				}
				setNombre(data?.nombre ?? "");
				setPuntosMinimos(data?.puntos_minimos?.toString?.() ?? "");
				setPuntosMaximos(data?.puntos_maximos?.toString?.() ?? "");
				setColor(data?.color ?? "verde");
			})
			.catch((e) => {
				if (cancelled) return;
				setError(e instanceof Error ? e.message : "Error cargando rango");
			})
			.finally(() => {
				if (cancelled) return;
				setLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, [rangoId]);

	async function handleSubmit(event) {
		event.preventDefault();
		setError("");
		setSuccessMessage("");

		if (!nombre || puntosMinimos === "" || puntosMaximos === "") {
			setError("Introduce todos los campos requeridos");
			return;
		}

		setLoading(true);
		try {
			const csrfRes = await fetch("/api/auth/csrf/", {
				method: "GET",
				credentials: "include",
			});
			if (!csrfRes.ok) {
				throw new Error("No se pudo obtener el token CSRF");
			}
			const { csrfToken } = await csrfRes.json();

			const payload = {
				nombre: nombre.trim(),
				color,
				puntos_minimos: Number(puntosMinimos),
				puntos_maximos: Number(puntosMaximos),
			};

			const endpoint = rangoId ? `/api/rangos/admin/${rangoId}/editar/` : "/api/rangos/admin/crear/";
			const method = rangoId ? "PUT" : "POST";
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
				const detail = data?.detail || "No se pudo guardar el rango";
				throw new Error(detail);
			}

			setSuccessMessage(rangoId ? "Rango actualizado" : "Rango creado");
			navigate("/admin/rangos");
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error guardando rango");
		} finally {
			setLoading(false);
		}
	}

	const selectClass = `rango-text rango-color-${(color ?? "")
		.replace(/_/g, "-")
		.toLowerCase()}`;

	return (
		<div className="app">
			<div className="admin-title-card">
				<h1 style={{ marginBottom: 0 }}>
					{mode === "edit" ? "ADMINISTRACION - EDITAR RANGO" : "ADMINISTRACION - CREAR RANGO"}
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
						<label htmlFor="puntosMinimos">Puntuacion minima *</label>
						<br />
						<input
							id="puntosMinimos"
							name="puntosMinimos"
							type="number"
							value={puntosMinimos}
							onChange={(e) => setPuntosMinimos(e.target.value)}
							disabled={loading}
						/>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="puntosMaximos">Puntuacion maxima *</label>
						<br />
						<input
							id="puntosMaximos"
							name="puntosMaximos"
							type="number"
							value={puntosMaximos}
							onChange={(e) => setPuntosMaximos(e.target.value)}
							disabled={loading}
						/>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="color">Color *</label>
						<br />
						<select
							id="color"
							name="color"
							value={color}
							onChange={(e) => setColor(e.target.value)}
							disabled={loading}
							className={selectClass}
						>
							{COLOR_OPTIONS.map((option) => (
								<option
									key={option.value}
									value={option.value}
									className={`rango-text rango-color-${option.value.replace(/_/g, "-")}`}
								>
									{option.label}
								</option>
							))}
						</select>
					</div>
					<div style={{ marginTop: 12 }}>
						<button type="submit" className="admin-primary-button">
							{mode === "edit" ? "Guardar cambios" : "Crear rango"}
						</button>
						<button
							type="button"
							className="admin-secondary-button"
							onClick={() => navigate("/admin/rangos")}
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
