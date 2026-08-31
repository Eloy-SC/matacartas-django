import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";
import defaultProfilePic from "../../assets/default_profile_pic.png";
import UserRango from "../../utils/UserRango.jsx";
import cabecera from "../../assets/cabecera.png";
import "../../styles/partidas.css";
import "../../styles/sala_espera.css";
import "../../styles/torneo.css";

const LONGITUD_LABELS = {
    express: "Express (5 manos)",
    corta: "Corta (20 manos)",
    normal: "Normal (40 manos)",
    larga: "Larga (60 manos)",
};

const COLORJUGADOR = {
    rojo: "red",
    naranja: "orange",
    amarillo: "goldenrod",
    verde: "green",
    azul: "blue",
    morado: "purple",
}

function formatBoolean(value) {
    if (typeof value !== "boolean") return "-";
    return value ? "Sí" : "No";
}

function formatDate(value) {
    if (!value) return "Pendiente";
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString("es-ES");
}

export default function Torneo() {
    const navigate = useNavigate();
    const { torneoId } = useParams();
    const [torneo, setTorneo] = useState(null);
    const [participantes, setParticipantes] = useState([]);
    const [userId, setUserId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [partidaActual, setPartidaActual] = useState(null);
    const [loadingPartidaActual, setLoadingPartidaActual] = useState(false);

    useEffect(() => {
        let cancelled = false;

        const loadTorneo = async () => {
            setLoading(true);
            setError("");

            try {
                const [torneoRes, participantesRes] = await Promise.all([
                    fetch(`/api/torneos/${torneoId}/`, { method: "GET", credentials: "include" }),
                    fetch(`/api/torneos/${torneoId}/participantes/`, { method: "GET", credentials: "include" }),
                ]);
                const torneoData = await torneoRes.json().catch(() => ({}));
                const participantesData = await participantesRes.json().catch(() => ([]));

                if (!torneoRes.ok) {
                    throw new Error(torneoData?.detail || "No se pudo cargar el torneo");
                }
                if (!participantesRes.ok) {
                    throw new Error(participantesData?.detail || "No se pudieron cargar los participantes");
                }

                if (!cancelled) {
                    setTorneo(torneoData);
                    setParticipantes(Array.isArray(participantesData) ? participantesData : []);
                }
            } catch (loadError) {
                if (!cancelled) {
                    setError(loadError instanceof Error ? loadError.message : "Error cargando el torneo");
                    setTorneo(null);
                    setParticipantes([]);
                }
            } finally {
                if (!cancelled) setLoading(false);
            }
        };

        void loadTorneo();
        return () => {
            cancelled = true;
        };
    }, [torneoId]);

    useEffect(() => {
		let cancelled = false;

		const loadCurrentUser = async () => {
			try {
				const res = await fetch("/api/auth/me/", {
					method: "GET",
					credentials: "include",
				});
				const data = await res.json().catch(() => ({}));

				if (!res.ok) {
					throw new Error(data?.detail || "No se pudo cargar el usuario actual");
				}

				if (!cancelled) {
					setUserId(data?.id ?? null);
				}
			} catch {
				if (!cancelled) {
					setUserId(null);
				}
			}
		};

		loadCurrentUser();

		return () => {
			cancelled = true;
		};
	}, []);

    useEffect(() => {
        let cancelled = false;

        const loadPartidaActual = async () => {
            // Solo cargar si el torneo ha iniciado y el usuario es participante
            if (!torneo?.fecha_inicio || !userId || !participantes.some(p => p.id === userId)) {
                return;
            }

            setLoadingPartidaActual(true);

            try {
                const res = await fetch(`/api/torneos/${torneoId}/partida_actual/`, {
                    method: "GET",
                    credentials: "include",
                });
                const data = await res.json().catch(() => ({}));

                if (!res.ok) {
                    // Si la llamada falla, no mostrar error (por ej, si el usuario no tiene partida asignada)
                    if (!cancelled) setPartidaActual(null);
                    return;
                }

                if (!cancelled) {
                    setPartidaActual(data);
                }
            } catch {
                if (!cancelled) {
                    setPartidaActual(null);
                }
            } finally {
                if (!cancelled) setLoadingPartidaActual(false);
            }
        };

        loadPartidaActual();
        return () => {
            cancelled = true;
        };
    }, [torneoId, torneo?.fecha_inicio, userId, participantes]);

    async function handleUnirseAlTorneo() {
        const csrfToken = await obtenerCsrfToken();

        try {
            const unirseRes = await fetch(
                `/api/torneos/${torneoId}/unirse/`,
                {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                }
            );

            if (!unirseRes.ok) {
                const unirseData = await unirseRes.json().catch(() => ({}));
                throw new Error(unirseData?.detail || "No se pudo unir al torneo");
            }
            alert("Te has unido al torneo. ¡Buena suerte!");
            window.location.reload();
        } catch (e) {
			alert(e instanceof Error ? e.message : "Error al procesar la unión");
		} finally {
			setJoiningPartidaId(null);
		}
    }

    async function handleAbandonarTorneo() {
        const csrfToken = await obtenerCsrfToken();

        try {
            const unirseRes = await fetch(
                `/api/torneos/${torneoId}/abandonar/`,
                {
                    method: "DELETE",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                }
            );

            if (!unirseRes.ok) {
                const unirseData = await unirseRes.json().catch(() => ({}));
                throw new Error(unirseData?.detail || "No se pudo abandonar el torneo");
            }
            alert("Has abandonado del torneo.");
            navigate("/torneos");
        } catch (e) {
			alert(e instanceof Error ? e.message : "Error al procesar la unión");
		} finally {
			setJoiningPartidaId(null);
		}
    }

    return (
        <div className="app torneo-page">
            <button className="partidas-volver-button" onClick={() => navigate("/torneos")}>
                ⮜
            </button>
            <img src={cabecera} alt="Matacartas" style={{ maxWidth: "100%", height: "auto" }} />

            {loading ? (
                <p className="torneo-message">Cargando...</p>
            ) : error ? (
                <p className="torneo-message" role="alert">{error}</p>
            ) : (
                <>
                    <div className="form-card torneo-details-card">
                        <h1>{torneo?.nombre ?? "Torneo"}</h1>
                        <div className="torneo-details-grid">
                            <div><span>Estado</span><strong>{torneo?.fecha_fin ? "Finalizado" : torneo?.fecha_inicio ? "En curso" : "Sin empezar"}</strong></div>
                            <div><span>Creado</span><strong>{formatDate(torneo?.fecha_creacion)}</strong></div>
                            <div><span>Inicio</span><strong>{formatDate(torneo?.fecha_inicio)}</strong></div>
                            <div><span>Longitud de partida</span><strong>{LONGITUD_LABELS[torneo?.partidas_longitud] ?? "-"}</strong></div>
                            <div><span>Jugadores por partida</span><strong>Final: {torneo?.num_jug_fin ?? "-"} · Semifinal: {torneo?.num_jug_sem ?? "-"}</strong></div>
                            <div><span>Fases anteriores</span><strong>Cuartos: {torneo?.num_jug_cua ?? "No"} · Octavos: {torneo?.num_jug_oct ?? "No"}</strong></div>
                            <div><span>Cartas especiales</span><strong>{formatBoolean(torneo?.partidas_cartas_especiales)}</strong></div>
                            <div><span>Tickets</span><strong>{formatBoolean(torneo?.partidas_tickets)}</strong></div>
                            <div><span>Tiempo máximo de turno</span><strong>{torneo?.partidas_tiempo_max_turno ?? "-"} s</strong></div>
                            <div><span>Desempate por puntuación</span><strong>{formatBoolean(torneo?.desempate_mayor_punt)}</strong></div>
                            <div><span>Medalla del primer puesto</span><strong>{torneo?.medalla_primer_puesto_nombre ?? "-"}</strong></div>
                            <div><span>Medalla del segundo puesto</span><strong>{torneo?.medalla_segundo_puesto_nombre ?? "-"}</strong></div>
                            <div><span>Medalla del tercer puesto</span><strong>{torneo?.medalla_tercer_puesto_nombre ?? "-"}</strong></div>
                        </div>
                    </div>




                    {!torneo?.fecha_inicio && !participantes.some(p => p.id === userId) ? (
                        <div style={{ marginBottom: 10 }}>
                            <button 
                                className="main-primary-button"
                                onClick={handleUnirseAlTorneo}
                                disabled={loading}
                            >
                                Unirse al torneo
                            </button>
                        </div>
                    ) : !torneo?.fecha_inicio && participantes.some(p => p.id === userId) ? (
                        <div style={{ marginBottom: 10 }}>
                            <button 
                                className="main-primary-button"
                                onClick={handleAbandonarTorneo}
                                disabled={loading}
                            >
                                Abandonar torneo
                            </button>
                        </div>
                    ) : null}

                    {torneo?.fecha_inicio && participantes.some(p => (p.id === userId && !p.eliminado)) && (
                        <div className="form-card" style={{ marginBottom: 20 }}>
                            {loadingPartidaActual ? (
                                <p className="torneo-message">Cargando partida...</p>
                            ) : partidaActual ? (
                                <>
                                    <h2 style={{ color: "#000" }}>{partidaActual.nombre ?? "-"}</h2>
                                    <div className="torneo-details-grid">
                                        <div><span>Inicio</span><strong>{formatDate(partidaActual.fecha_inicio)}</strong></div>
                                        <div><span>Fin</span><strong>{formatDate(partidaActual.fecha_fin)}</strong></div>
                                    </div>
                                    <div style={{ marginTop: 20 }}>
                                        <h3 style={{ marginBottom: 15 }}>Jugadores en la partida</h3>
                                        <div className="torneo-participants-grid">
                                            {Object.entries(partidaActual.jugadores || {}).map(([color, jugador]) => (
                                                <article className="sala-espera-player-card" key={color}>
                                                    <img 
                                                    className="sala-espera-player-card__avatar" 
                                                    src={jugador.imagen || defaultProfilePic} 
                                                    style={{ borderColor: COLORJUGADOR[jugador?.color] || "black" }}
                                                    alt={`Foto de perfil de ${jugador.nombre ?? "jugador"}`} 
                                                    onError={(event) => { event.currentTarget.src = defaultProfilePic; }} />
                                                    <div className="sala-espera-player-card__content">
                                                        <strong className="sala-espera-player-card__name">
                                                            {jugador.nombre || "Jugador"}
                                                        </strong>
                                                        <span className="sala-espera-player-card__rango">
                                                            <UserRango userId={jugador.id} />
                                                        </span>
                                                        {partidaActual.fecha_fin && (
                                                            <span className="sala-espera-player-card__score" style={{ fontSize: "0.9em", color: "#666" }}>
                                                                Puntos: {jugador.puntos ?? 0}
                                                            </span>
                                                        )}
                                                    </div>
                                                </article>
                                            ))}
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => navigate(`/partidas/mesa/${partidaActual.partida_id}/`)}
                                        className="main-primary-button"
                                        style={{ marginTop: 20 }}
                                        disabled={loadingPartidaActual || partidaActual.fecha_fin !== null}
                                    >
                                        Jugar
                                    </button>
                                </>
                            ) : (
                                <p className="torneo-message">No hay una partida asignada en este momento.</p>
                            )}
                        </div>
                    )}

                        <div className="form-card torneo-participants-card">
                            <h2>Participantes ({participantes.length})</h2>
                            <div className="torneo-participants-grid">
                                {participantes.length === 0 ? <p className="torneo-message">Todavía no hay participantes.</p> : participantes.map((participante) => (
                                    <article className={`sala-espera-player-card ${
												participante.id === userId ? "sala-espera-player-card--me" : ""
											}`} key={participante.id}>
                                        <img className="sala-espera-player-card__avatar" src={participante.imagen || defaultProfilePic} alt={`Foto de perfil de ${participante.nombre ?? "jugador"}`} onError={(event) => { event.currentTarget.src = defaultProfilePic; }} />
                                        <div className="sala-espera-player-card__content">
                                            {participante.eliminado && (
                                                <strong className="sala-espera-player-card__name" style={{ color: "red" }}>
                                                    ELIMINADO
                                                </strong>
                                            )}
                                            <strong className="sala-espera-player-card__name">
                                                {participante.creador ? " 👑" : ""}
                                                {participante.nombre || "Participante"}
                                            </strong>
                                            <span className="sala-espera-player-card__rango">
                                                <UserRango userId={participante.id} />
                                            </span>
                                        </div>
                                    </article>
                                ))}
                            </div>
                        </div>
                </>
            )}
        </div>
    );
}