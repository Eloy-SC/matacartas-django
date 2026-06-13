import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import defaultProfilePic from "../../assets/default_profile_pic.png";
import cabecera from "../../assets/cabecera.png";
import "../../styles/partidas.css";

function formatBoolean(value) {
	if (typeof value === "boolean") {
		return value ? "Sí" : "No";
	}
	if (value === null || value === undefined) {
		return "-";
	}
	return String(value);
}

function splitPlayersIntoRows(players) {
	if (players.length <= 1) {
		return [players];
	}

	const firstRowSize = Math.ceil(players.length / 2);
	return [players.slice(0, firstRowSize), players.slice(firstRowSize)];
}

export default function SalaEsperaPartida() {
	const navigate = useNavigate();
	const { partidaId } = useParams();
	const [partida, setPartida] = useState(null);
	const [jugadores, setJugadores] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	useEffect(() => {
		let cancelled = false;

		async function loadSalaEspera() {
			setLoading(true);
			setError("");

			try {
				const [partidaRes, jugadoresRes] = await Promise.all([
					fetch(`/api/partidas/${partidaId}/jugador/`, {
						method: "GET",
						credentials: "include",
					}),
					fetch(`/api/partidas/${partidaId}/jugadores/`, {
						method: "GET",
						credentials: "include",
					}),
				]);

				const partidaData = await partidaRes.json().catch(() => ({}));
				const jugadoresData = await jugadoresRes.json().catch(() => ([]));

				if (!partidaRes.ok) {
					throw new Error(partidaData?.detail || "No se pudo cargar la partida");
				}
				if (!jugadoresRes.ok) {
					throw new Error(jugadoresData?.detail || "No se pudo cargar la lista de jugadores");
				}

				const jugadoresBase = Array.isArray(jugadoresData) ? jugadoresData : [];
				const jugadoresConRango = await Promise.all(
					jugadoresBase.map(async (jugador) => {
						if (!jugador?.id) {
							return {
								...jugador,
								rango_nombre: "",
							};
						}

						try {
							const rangoRes = await fetch(`/api/rangos/usuario/${jugador.id}/`, {
								method: "GET",
								credentials: "include",
							});
							const rangoData = await rangoRes.json().catch(() => ({}));
							if (!rangoRes.ok) {
								return {
									...jugador,
									rango_nombre: "",
								};
							}

							return {
								...jugador,
								rango_nombre: rangoData?.nombre ?? "",
							};
						} catch {
							return {
								...jugador,
								rango_nombre: "",
							};
						}
					})
				);

				if (cancelled) return;
				setPartida(partidaData);
				setJugadores(jugadoresConRango);
			} catch (e) {
				if (cancelled) return;
				setError(e instanceof Error ? e.message : "Error cargando la sala de espera");
				setPartida(null);
				setJugadores([]);
			} finally {
				if (cancelled) return;
				setLoading(false);
			}
		}

		loadSalaEspera();

		return () => {
			cancelled = true;
		};
	}, [partidaId]);

	const playerRows = useMemo(() => splitPlayersIntoRows(jugadores), [jugadores]);

	return (
		<div className="app sala-espera-page">
			<button
				type="button"
				className="partidas-volver-button"
				onClick={() => navigate(-1)}
				aria-label="Volver"
			>
				⮜
			</button>
			<img src={cabecera} alt="Matacartas" style={{ maxWidth: "100%", height: "auto" }} />

			<div className="sala-espera-card">
				<h1 className="partidas-title-card sala-espera-title">Sala de espera</h1>

				{loading ? (
					<p className="sala-espera-message">Cargando...</p>
				) : error ? (
					<p className="sala-espera-message" role="alert">
						{error}
					</p>
				) : (
					<>
						<div className="sala-espera-stats">
							<div className="sala-espera-stat">
								<span className="sala-espera-stat__label">Número de jugadores</span>
								<span className="sala-espera-stat__value">{partida?.num_jugadores ?? "-"}</span>
							</div>
							<div className="sala-espera-stat">
								<span className="sala-espera-stat__label">Longitud</span>
								<span className="sala-espera-stat__value">{partida?.longitud ?? "-"}</span>
							</div>
							<div className="sala-espera-stat">
								<span className="sala-espera-stat__label">Cartas invencibles</span>
								<span className="sala-espera-stat__value">{formatBoolean(partida?.cartas_invencibles)}</span>
							</div>
							<div className="sala-espera-stat">
								<span className="sala-espera-stat__label">Tiempo máximo de turno</span>
								<span className="sala-espera-stat__value">{partida?.tiempo_max_turno ?? "-"} s</span>
							</div>
						</div>

						<div className="sala-espera-grid" aria-label="Jugadores de la partida">
							{playerRows.map((row, rowIndex) => (
								<div
									key={`row-${rowIndex}`}
									className="sala-espera-grid__row"
									style={{ gridTemplateColumns: `repeat(${row.length}, max-content)` }}
								>
									{row.map((jugador) => (
										<article key={jugador.id ?? jugador.nombre} className="sala-espera-player-card">
											<img
												className="sala-espera-player-card__avatar"
												src={jugador.imagen || defaultProfilePic}
												alt={`Foto de perfil de ${jugador.nombre ?? "jugador"}`}
												onError={(event) => {
													event.currentTarget.src = defaultProfilePic;
												}}
											/>
											<div className="sala-espera-player-card__content">
												<strong className="sala-espera-player-card__name">{jugador.nombre ?? "Sin nombre"}</strong>
												<span className="sala-espera-player-card__rango">
													{jugador.rango_nombre || "Sin rango"}
												</span>
											</div>
										</article>
									))}
								</div>
							))}
						</div>
					</>
				)}
			</div>
		</div>
	);
}
