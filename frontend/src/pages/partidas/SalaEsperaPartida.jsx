import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import defaultProfilePic from "../../assets/default_profile_pic.png";
import cabecera from "../../assets/cabecera.png";
import EdicionPartidaSE from "./EdicionPartidaSE.jsx";
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
	const [userId, setUserId] = useState(null);
	const [isEditModalOpen, setIsEditModalOpen] = useState(false);

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

	const loadSalaEspera = async ({ showLoading = true } = {}) => {
		if (showLoading) {
			setLoading(true);
			setError("");
		}

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

			console.log("JUGADORES:", jugadoresData);

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

			setPartida(partidaData);
			setJugadores(jugadoresConRango);
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error cargando la sala de espera");
			setPartida(null);
			setJugadores([]);
		} finally {
			if (showLoading) {
				setLoading(false);
			}
		}
	};

	const handleAbandonarSala = async (partidaId) => {
		try {
			// Primero verificar si ya participa en la partida
			const participaRes = await fetch(`/api/partidas/${partidaId}/participa/`, {
				method: "GET",
				credentials: "include",
			});

			if (!participaRes.ok) {
				navigate("/partidas");
				return;
			}

			const participaData = await participaRes.json().catch(() => ({}));

			if (!participaData?.participa) {
				// No participa, ir a lista de partidas
				navigate("/partidas");
				return;
			}

			// Participa, intentar abandonar
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

			const abandonarRes = await fetch(`/api/partidas/${partidaId}/abandonar/`, {
				method: "DELETE",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
			});

			if (!abandonarRes.ok) {
				const abandonarData = await abandonarRes.json().catch(() => ({}));
				throw new Error(abandonarData?.detail || "No se pudo abandonar la partida");
			}

			// Abandono exitoso, ir a la lista de partidas
			navigate("/partidas");
		} catch (e) {
			alert(e instanceof Error ? e.message : "Error al procesar el abandono");
		}
	};

	const handleToggleListo = async (partidaId) => {
		try {
			// Primero verificar si ya participa en la partida
			const participaRes = await fetch(`/api/partidas/${partidaId}/participa/`, {
				method: "GET",
				credentials: "include",
			});

			if (!participaRes.ok) {
				navigate("/partidas");
				return;
			}

			const participaData = await participaRes.json().catch(() => ({}));

			if (!participaData?.participa) {
				// No participa, ir a lista de partidas
				navigate("/partidas");
				return;
			}

			// Participa, intentar marcar como listo
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

			const toggleListoRes = await fetch(`/api/partidas/${partidaId}/toggle-listo/`, {
				method: "PUT",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
			});

			if (!toggleListoRes.ok) {
				const toggleListoData = await toggleListoRes.json().catch(() => ({}));
				throw new Error(toggleListoData?.detail || "No se pudo cambiar el estado de listo");
			}

			// Refresco exitoso sin indicador de carga
			await loadSalaEspera({ showLoading: false });
		} catch (e) {
			alert(e instanceof Error ? e.message : "Error al procesar el cambio del estado de listo");
		}
	};

	const handleExpulsarJugador = async (jugadorId) => {
		try {
			// Expulsar al jugador
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

			const expulsarRes = await fetch(`/api/partidas/${partidaId}/expulsar-jugador/${jugadorId}/`, {
				method: "DELETE",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
			});

			if (!expulsarRes.ok) {
				const expulsarData = await expulsarRes.json().catch(() => ({}));
				throw new Error(expulsarData?.detail || "No se pudo expulsar al jugador");
			}

			// Expulsión exitosa, refrescar la sala de espera
			await loadSalaEspera({ showLoading: false });
		} catch (e) {
			alert(e instanceof Error ? e.message : "Error al procesar la expulsión del jugador");
		}
	};

	useEffect(() => {
		const loadInitial = async () => {
			await loadSalaEspera({ showLoading: true });
		};

		loadInitial();
	}, [partidaId]);

	useEffect(() => {
		const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
		let socket;
		let reconnectTimer;
		let shouldReconnect = true;

		const connect = () => {
			socket = new WebSocket(
				`${protocol}//${window.location.host}/ws/partidas/${partidaId}/`
			);

			socket.onopen = () => {
				console.log("WS conectado");
			};

			socket.onmessage = async (event) => {
				const data = JSON.parse(event.data);

				if (data.type === "room_updated") {
					await loadSalaEspera({ showLoading: false });
				}
			};

			socket.onclose = () => {
				if (!shouldReconnect) {
					return;
				}

				console.log("WS cerrado, reintentando...");
				reconnectTimer = setTimeout(connect, 3000);
			};
		};

		connect();

		return () => {
			shouldReconnect = false;
			clearTimeout(reconnectTimer);
			socket?.close();
		};
	}, [partidaId]);

	const playerRows = useMemo(() => splitPlayersIntoRows(jugadores), [jugadores]);
	const jugadorActual = useMemo(
		() => jugadores.find((jugador) => jugador.id === userId),
		[jugadores, userId]
	);

	const handleOpenEditModal = () => {
		if (partida) {
			setIsEditModalOpen(true);
		}
	};

	const handleCloseEditModal = () => {
		setIsEditModalOpen(false);
	};

	const handlePartidaUpdated = async () => {
		await loadSalaEspera({ showLoading: false });
	};

	return (
		<div className="app sala-espera-page">
			<img src={cabecera} alt="Matacartas" style={{ maxWidth: "100%", height: "auto" }} />

			<div className="sala-espera-card">
				{loading ? (
					<p className="sala-espera-message">Cargando...</p>
				) : error ? (
					<p className="sala-espera-message" role="alert">
						{error}
					</p>
				) : (
					<>
						<EdicionPartidaSE
							isOpen={isEditModalOpen}
							partida={partida}
							onClose={handleCloseEditModal}
							onSaved={handlePartidaUpdated}
						/>
						<h1 className="sala-espera-title">Sala de espera: {partida?.nombre}</h1>
						{partida?.privada && (<h2 className="sala-espera-subtitle">Clave de la partida: {partida?.clave}</h2>)}
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

							{jugadorActual?.creador && (
								<button
									type="button"
									className="partidas-primary-button"
									onClick={handleOpenEditModal}
								>
										Editar partida
								</button>
							)}
						</div>

						<div className="sala-espera-grid" aria-label="Jugadores de la partida">
							{playerRows.map((row, rowIndex) => (
								<div
									key={`row-${rowIndex}`}
									className="sala-espera-grid__row"
									style={{ gridTemplateColumns: `repeat(${row.length}, max-content)` }}
								>
									{row.map((jugador) => (
										<article
											key={jugador.id ?? jugador.nombre}
											className={`sala-espera-player-card ${
												jugador.id === userId ? "sala-espera-player-card--me" : ""
											}`}
										>
											{jugadorActual?.creador && jugador.id !== userId && (
												<button
													type="button"
													aria-label="Expulsar jugador"
													onClick={() => handleExpulsarJugador(jugador.id)}
													className="kick-player-button"
												>
													X
											</button>)}
											<img
												className="sala-espera-player-card__avatar"
												src={jugador.imagen || defaultProfilePic}
												alt={`Foto de perfil de ${jugador.nombre ?? "jugador"}`}
												onError={(event) => {
													event.currentTarget.src = defaultProfilePic;
												}}
											/>
											<div className="sala-espera-player-card__content">
												<strong className="sala-espera-player-card__name">
													{jugador.nombre ?? "Sin nombre"}
													{jugador.creador ? " 👑" : ""}
												</strong>
												<span className="sala-espera-player-card__rango">
													{jugador.rango_nombre || "Sin rango"}
												</span>
												<span className="sala-espera-player-card__listo" style={{ fontWeight: "bold", color: jugador.listo ? "green" : "red" }}>
													{jugador.listo ? "Listo" : "No listo"}
												</span>
											</div>
										</article>
									))}
								</div>
							))}
						</div>
						<div>
							<button
								type="button"
								className="main-primary-button"
								onClick={() => handleAbandonarSala(partidaId)}
								aria-label="Volver"
								disabled={loading}
							>
								Abandonar sala de espera
							</button>
							<button
								type="button"
								className="main-primary-button"
								onClick={() => handleToggleListo(partidaId)}
								aria-label="Marcar como listo"
								disabled={loading}
							>
									{jugadorActual?.listo ? "Marcar \"no listo\"" : "Marcar \"listo\""}
							</button>
						</div>
					</>
				)}
			</div>
		</div>
	);
}
