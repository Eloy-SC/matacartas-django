import { useEffect, useMemo, useState } from "react";
import { formatApiError } from "../../utils/ApiErrors.jsx";

const JUGADORES_OPTIONS = [2, 3, 4, 5, 6];

const LONGITUD_OPTIONS = [
	{ value: "corta", label: "Corta (20 manos)" },
	{ value: "normal", label: "Normal (40 manos)" },
	{ value: "larga", label: "Larga (60 manos)" },
];

function toSelectValue(value) {
	if (value === null || value === undefined) {
		return "";
	}
	return String(value);
}

export default function EdicionPartidaSE({ isOpen, partida, onClose, onSaved }) {
	const [rangos, setRangos] = useState([]);
	const [rangosLoading, setRangosLoading] = useState(false);
	const [rangosError, setRangosError] = useState("");
	const [nombre, setNombre] = useState("");
	const [numJugadores, setNumJugadores] = useState("2");
	const [longitud, setLongitud] = useState("normal");
	const [cartasEspeciales, setCartasEspeciales] = useState(true);
	const [tickets, setTickets] = useState(true);
	const [tiempoMaxTurno, setTiempoMaxTurno] = useState("90");
	const [privada, setPrivada] = useState(false);
	const [clave, setClave] = useState("");
	const [rangoMinimoId, setRangoMinimoId] = useState("");
	const [rangoMaximoId, setRangoMaximoId] = useState("");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");

	const partidaId = partida?.id;
	const rangePlaceholder = useMemo(() => {
		if (rangosLoading) {
			return "Cargando rangos...";
		}
		if (rangosError) {
			return "Error cargando rangos";
		}
		return "Sin selección";
	}, [rangosLoading, rangosError]);

	useEffect(() => {
		if (!isOpen || !partida) {
			return;
		}

		setNombre(partida?.nombre ?? "");
		setNumJugadores(toSelectValue(partida?.num_jugadores ?? 2));
		setLongitud(partida?.longitud ?? "normal");
		setCartasEspeciales(Boolean(partida?.cartas_especiales));
		setTickets(Boolean(partida?.tickets));
		setTiempoMaxTurno(toSelectValue(partida?.tiempo_max_turno ?? 90));
		setPrivada(Boolean(partida?.privada));
		setClave(partida?.clave ?? "");
		setRangoMinimoId(toSelectValue(partida?.rango_minimo_id));
		setRangoMaximoId(toSelectValue(partida?.rango_maximo_id));
		setError("");
	}, [isOpen, partida]);

	useEffect(() => {
		if (!isOpen) {
			return;
		}

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
					throw new Error(data?.detail || "No se pudieron cargar los rangos");
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
	}, [isOpen]);

	if (!isOpen || !partida) {
		return null;
	}

	async function handleSubmit(event) {
		event.preventDefault();
		setError("");

		const nombreTrimmed = nombre.trim();
		const claveTrimmed = clave.trim();
		const numJugadoresNumber = Number(numJugadores);
		const tiempoMaxTurnoNumber = Number(tiempoMaxTurno);

		if (!nombreTrimmed) {
			setError("Introduce el titulo de la partida");
			return;
		}

		if (Number.isNaN(numJugadoresNumber)) {
			setError("El numero de jugadores no es valido");
			return;
		}

		if (Number.isNaN(tiempoMaxTurnoNumber)) {
			setError("El tiempo maximo no es valido");
			return;
		}

		if (privada && !claveTrimmed) {
			setError("Introduce la clave para la partida privada");
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

			const { csrfToken } = await csrfRes.json().catch(() => ({}));
			if (!csrfToken) {
				throw new Error("Token CSRF no disponible");
			}

			const payload = {
				nombre: nombreTrimmed,
				num_jugadores: numJugadoresNumber,
				longitud,
				cartas_especiales: Boolean(cartasEspeciales),
				tickets: Boolean(tickets),
				tiempo_max_turno: tiempoMaxTurnoNumber,
				privada,
				clave: privada ? claveTrimmed || null : null,
				rango_minimo_id: rangoMinimoId ? Number(rangoMinimoId) : null,
				rango_maximo_id: rangoMaximoId ? Number(rangoMaximoId) : null,
			};

			const res = await fetch(`/api/partidas/${partidaId}/editar/`, {
				method: "PUT",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
				body: JSON.stringify(payload),
			});

			const data = await res.json().catch(() => ({}));
			if (!res.ok) {
				throw new Error(formatApiError(data) || "No se pudo guardar la partida");
			}

			if (onSaved) {
				await onSaved(data);
			}
			onClose();
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error guardando partida");
		} finally {
			setLoading(false);
		}
	}

	return (
		<div
			className="sala-espera-edit-modal__overlay"
			role="presentation"
			onClick={(event) => {
				if (event.target === event.currentTarget && !loading) {
					onClose();
				}
			}}
		>
			<div className="sala-espera-edit-modal" role="dialog" aria-modal="true" aria-labelledby="edicion-partida-title">
				<h2 id="edicion-partida-title" className="sala-espera-edit-modal__title">
					Editar partida
				</h2>
				<form className="sala-espera-edit-modal__form" onSubmit={handleSubmit}>
					<div className="sala-espera-edit-modal__field">
						<label htmlFor="editarNombre">Titulo de la partida</label>
						<input
							id="editarNombre"
							type="text"
							maxLength={40}
							value={nombre}
							onChange={(event) => setNombre(event.target.value)}
							disabled={loading}
						/>
					</div>

					<div className="sala-espera-edit-modal__grid">
						<div className="sala-espera-edit-modal__field">
							<label htmlFor="editarJugadores">Numero de jugadores</label>
							<select
								id="editarJugadores"
								value={numJugadores}
								onChange={(event) => setNumJugadores(event.target.value)}
								disabled={loading}
							>
								{JUGADORES_OPTIONS.map((value) => (
									<option key={value} value={value}>
										{value}
									</option>
								))}
							</select>
						</div>

						<div className="sala-espera-edit-modal__field">
							<label htmlFor="editarLongitud">Longitud</label>
							<select
								id="editarLongitud"
								value={longitud}
								onChange={(event) => setLongitud(event.target.value)}
								disabled={loading}
							>
								{LONGITUD_OPTIONS.map((option) => (
									<option key={option.value} value={option.value}>
										{option.label}
									</option>
								))}
							</select>
						</div>
					</div>

					<div className="sala-espera-edit-modal__grid">
						<div className="sala-espera-edit-modal__field">
							<label htmlFor="editarTiempo">Tiempo maximo por turno</label>
							<input
								id="editarTiempo"
								type="number"
								min="1"
								value={tiempoMaxTurno}
								onChange={(event) => setTiempoMaxTurno(event.target.value)}
								disabled={loading}
							/>
						</div>

						<div className="sala-espera-edit-modal__field sala-espera-edit-modal__field--checkbox">
							<label htmlFor="editarCartasEspeciales">Cartas especiales</label>
							<input
								id="editarCartasEspeciales"
								type="checkbox"
								checked={cartasEspeciales}
								onChange={(event) => setCartasEspeciales(event.target.checked)}
								disabled={loading}
							/>
						</div>

						<div className="sala-espera-edit-modal__field sala-espera-edit-modal__field--checkbox">
							<label htmlFor="editarTickets">Tickets</label>
							<input
								id="editarTickets"
								type="checkbox"
								checked={tickets}
								onChange={(event) => setTickets(event.target.checked)}
								disabled={loading}
							/>
						</div>
					</div>

					<div className="sala-espera-edit-modal__grid">
						<div className="sala-espera-edit-modal__field">
							<label htmlFor="editarRangoMinimo">Rango minimo</label>
							<select
								id="editarRangoMinimo"
								disabled={loading}
							/>
						</div>
					</div>

					<div className="sala-espera-edit-modal__grid">
						<div className="sala-espera-edit-modal__field">
							<label htmlFor="editarRangoMinimo">Rango minimo</label>
							<select
								id="editarRangoMinimo"
								value={rangoMinimoId}
								onChange={(event) => setRangoMinimoId(event.target.value)}
								disabled={loading || rangosLoading || Boolean(rangosError)}
							>
								<option value="">{rangePlaceholder}</option>
								{rangos.map((rango) => (
									<option key={rango.id} value={rango.id}>
										{rango.nombre}
									</option>
								))}
							</select>
						</div>

						<div className="sala-espera-edit-modal__field">
							<label htmlFor="editarRangoMaximo">Rango maximo</label>
							<select
								id="editarRangoMaximo"
								value={rangoMaximoId}
								onChange={(event) => setRangoMaximoId(event.target.value)}
								disabled={loading || rangosLoading || Boolean(rangosError)}
							>
								<option value="">{rangePlaceholder}</option>
								{rangos.map((rango) => (
									<option key={rango.id} value={rango.id}>
										{rango.nombre}
									</option>
								))}
							</select>
						</div>
					</div>

					<div className="sala-espera-edit-modal__field sala-espera-edit-modal__field--checkbox">
						<label htmlFor="editarPrivada">Partida privada</label>
						<input
							id="editarPrivada"
							type="checkbox"
							checked={privada}
							onChange={(event) => {
								const checked = event.target.checked;
								setPrivada(checked);
								if (!checked) {
									setClave("");
								}
							}}
							disabled={loading}
						/>
					</div>

					{privada && (
						<div className="sala-espera-edit-modal__field">
							<label htmlFor="editarClave">Clave</label>
							<input
								id="editarClave"
								type="text"
								value={clave}
								onChange={(event) => setClave(event.target.value)}
								disabled={loading}
							/>
						</div>
					)}

					<div className="sala-espera-edit-modal__actions">
						<button type="submit" className="partidas-primary-button" disabled={loading || rangosLoading}>
							{loading ? "Guardando..." : "Aceptar"}
						</button>
						<button
							type="button"
							className="partidas-primary-button"
							onClick={onClose}
							disabled={loading}
						>
							Cancelar
						</button>
					</div>

					{error && (
						<p className="sala-espera-edit-modal__error" role="alert">
							{error}
						</p>
					)}
					{rangosError && (
						<p className="sala-espera-edit-modal__error" role="status">
							{rangosError}
						</p>
					)}
				</form>
			</div>
		</div>
	);
}
