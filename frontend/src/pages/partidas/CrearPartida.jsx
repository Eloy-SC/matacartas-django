import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import cabecera from "../../assets/cabecera.png";
import "../../styles/partidas.css";

const JUGADORES_OPTIONS = [2, 3, 4, 5, 6];

const LONGITUD_OPTIONS = [
	{ value: "corta", label: "Corta (20 manos)" },
	{ value: "normal", label: "Normal (40 manos)" },
	{ value: "larga", label: "Larga (60 manos)" },
];

export default function CrearPartida() {
    const navigate = useNavigate();
	const [rangos, setRangos] = useState([]);
	const [rangosLoading, setRangosLoading] = useState(true);
	const [rangosError, setRangosError] = useState("");
	const [isPrivada, setIsPrivada] = useState(false);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [successMessage, setSuccessMessage] = useState("");

	useEffect(() => {
		let cancelled = false;
		setRangosLoading(true);
		setRangosError("");

		fetch("/api/rangos/listar/", {
			method: "GET",
			credentials: "include",
		})
			.then(async (res) => {
				const data = await res.json().catch(() => ([]));
				if (cancelled) return;
				if (!res.ok) {
					const detail = data?.detail || "No se pudieron cargar los rangos";
					throw new Error(detail);
				}
				setRangos(Array.isArray(data) ? data : []);
			})
			.catch((e) => {
				if (cancelled) return;
				setRangosError(e instanceof Error ? e.message : "Error cargando rangos");
				setRangos([]);
			})
			.finally(() => {
				if (cancelled) return;
				setRangosLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, []);

	const rangoPlaceholder = rangosLoading
		? "Cargando rangos..."
		: rangosError
			? "Error cargando rangos"
			: "Selecciona un rango";

	async function handleSubmit(event) {
		event.preventDefault();
		setError("");
		setSuccessMessage("");

		const formData = new FormData(event.currentTarget);
		const nombre = `${formData.get("titulo") ?? ""}`.trim();
		const numJugadoresValue = formData.get("jugadores");
		const tiempoValue = formData.get("tiempoMaximo");
		const rangoMinimoValue = formData.get("rangoMinimo");
		const rangoMaximoValue = formData.get("rangoMaximo");
		const claveValue = `${formData.get("clave") ?? ""}`.trim();
		const privada = isPrivada;

		if (!nombre) {
			setError("Introduce el titulo de la partida");
			return;
		}

		const num_jugadores = numJugadoresValue ? Number(numJugadoresValue) : 2;
		if (Number.isNaN(num_jugadores)) {
			setError("El numero de jugadores no es valido");
			return;
		}

		const tiempo_max_turno = tiempoValue ? Number(tiempoValue) : 90;
		if (Number.isNaN(tiempo_max_turno)) {
			setError("El tiempo maximo no es valido");
			return;
		}

		if (privada && !claveValue) {
			setError("Introduce la clave para la partida privada");
			return;
		}

		const payload = {
			nombre,
			num_jugadores,
			longitud: formData.get("longitud") || "normal",
			cartas_invencibles: Boolean(formData.get("cartasInvencibles")),
			tiempo_max_turno,
			privada,
			clave: privada ? claveValue || null : null,
			rango_minimo_id: rangoMinimoValue ? Number(rangoMinimoValue) : null,
			rango_maximo_id: rangoMaximoValue ? Number(rangoMaximoValue) : null,
		};

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

			const res = await fetch("/api/partidas/crear/", {
				method: "POST",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
				body: JSON.stringify(payload),
			});

			const data = await res.json().catch(() => ({}));
			if (!res.ok) {
				const detail = data?.detail || "No se pudo crear la partida";
				throw new Error(detail);
			}

			setSuccessMessage("Partida creada");
			navigate("/partidas");
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error creando partida");
		} finally {
			setLoading(false);
		}
	}

	return (
		<div className="app">
            <button className="partidas-volver-button" onClick={() => navigate("/inicio")}>⮜</button>
			<img src={cabecera} alt="Matacartas" style={{ maxWidth: "100%", height: "auto" }} />
			<div className="form-card">
				<form onSubmit={handleSubmit}>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="titulo">Titulo de la partida</label>
						<br />
						<input
							id="titulo"
							name="titulo"
							type="text"
							maxLength={40}
							placeholder="Hasta 40 caracteres"
						/>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="jugadores">Numero de jugadores</label>
						<br />
						<select id="jugadores" name="jugadores">
							{JUGADORES_OPTIONS.map((value) => (
								<option key={value} value={value}>
									{value}
								</option>
							))}
						</select>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="longitud">Longitud</label>
						<br />
						<select id="longitud" name="longitud" defaultValue="normal">
							{LONGITUD_OPTIONS.map((option) => (
								<option key={option.value} value={option.value}>
									{option.label}
								</option>
							))}
						</select>
					</div>
					<div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8 }}>
						<input id="cartasInvencibles" name="cartasInvencibles" type="checkbox" />
						<label htmlFor="cartasInvencibles">Cartas invencibles</label>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="tiempoMaximo">Tiempo maximo por turno (segundos)</label>
						<br />
						<input
							id="tiempoMaximo"
							name="tiempoMaximo"
							type="number"
							defaultValue={90}
						/>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="rangoMinimo">Rango minimo</label>
						<br />
						<select
							id="rangoMinimo"
							name="rangoMinimo"
							disabled={rangosLoading || Boolean(rangosError)}
						>
							<option value="">{rangoPlaceholder}</option>
							{rangos.map((rango) => (
								<option key={rango.id} value={rango.id}>
									{rango.nombre}
								</option>
							))}
						</select>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="rangoMaximo">Rango maximo</label>
						<br />
						<select
							id="rangoMaximo"
							name="rangoMaximo"
							disabled={rangosLoading || Boolean(rangosError)}
						>
							<option value="">{rangoPlaceholder}</option>
							{rangos.map((rango) => (
								<option key={rango.id} value={rango.id}>
									{rango.nombre}
								</option>
							))}
						</select>
					</div>
					<div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8 }}>
						<input
							id="partidaPrivada"
							name="partidaPrivada"
							type="checkbox"
							checked={isPrivada}
							onChange={(event) => setIsPrivada(event.target.checked)}
						/>
						<label htmlFor="partidaPrivada">Partida privada</label>
					</div>
					{isPrivada && (
						<div style={{ marginTop: 12 }}>
							<label htmlFor="clave">Clave</label>
							<br />
							<input id="clave" name="clave" type="text" />
						</div>
					)}
					<div style={{ marginTop: 16 }}>
						<button
							type="submit"
							className="partidas-primary-button"
							disabled={loading || rangosLoading}
						>
							{loading ? "Creando..." : "Crear"}
						</button>
					</div>
					{error && (
						<p role="alert" style={{ marginTop: 12, color: "red", fontWeight: "bold" }}>
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
