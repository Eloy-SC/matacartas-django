import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import CartasPropias from "./CartasPropias.jsx";
import TicketJugador from "./TicketJugador.jsx";
import {
	handleCambiarCartas,
	handleEleccionCambio,
	handleEleccionComodin,
	handleJugarCarta,
	handleToggleCartaSeleccionada,
	handleToggleCartaSeleccionadaUnica,
	handleRetirarseDeMano,
} from "./FuncionesMesa.js";
import CartasEnMesa from "./CartasEnMesa.jsx";
import InfoSuperior from "./InfoSuperior.jsx";
import MesaInicialContrincantes from "./MesaInicialContrincantes.jsx";
import ResumenManoPanel from "./ResumenManoPanel.jsx";
import ResumenPartidaOverlay from "./ResumenPartidaOverlay.jsx";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";
import "../../styles/mesa.css";

const COLORJUGADOR = {
    rojo: "red",
    naranja: "orange",
    amarillo: "goldenrod",
    verde: "green",
    azul: "blue",
    morado: "purple",
}

export default function Juego() {
	const { partidaId } = useParams();
	const [mesa, setMesa] = useState(null);
	const [mesaInicial, setMesaInicial] = useState(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [cartasSeleccionadas, setCartasSeleccionadas] = useState([]);
	const [cartaComodinSeleccionada, setCartaComodinSeleccionada] = useState(null);
	const [cuentaAtrasTurno, setCuentaAtrasTurno] = useState(null);
	const [cuentaAtrasFinMano, setCuentaAtrasFinMano] = useState(null);
	const [manoFinalizadaId, setManoFinalizadaId] = useState(null);
	const [resumenMano, setResumenMano] = useState(null);
	const [cargandoResumenMano, setCargandoResumenMano] = useState(false);
	const [errorResumenMano, setErrorResumenMano] = useState("");
	const [datosFinalPartida, setDatosFinalPartida] = useState(null);
	const finManoProgramadaRef = useRef(null);
	const resumenManoSolicitadoRef = useRef(null);
	const resumenFinalSolicitadoRef = useRef(false);
	const accionAutomaticaTurnoClaveRef = useRef(null);
	const accionAutomaticaTurnoEjecutadaRef = useRef(null);
	const accionAutomaticaTurnoEnCursoRef = useRef(false);

	const partida = mesa?.partida ?? null;
	const mano = mesa?.mano ?? null;
	const jugador = mesa?.jugador ?? null;
	const contrincantes = mesa?.contrincantes ?? [];
	const rondas = mesa?.rondas ?? [];
	const rondaActual = rondas[rondas.length - 1] ?? null;
	const rondaCambio = rondas.length === 1 ? rondas[0] : null;
	const esTurnoJugador = Boolean(partida?.turno_actual && jugador?.color && partida.turno_actual === jugador.color);
	const puedeJugarCarta =
		esTurnoJugador &&
		Boolean(rondaActual && rondaActual.ronda_num >= 1 && rondaActual.ronda_num <= 3);
	const puedeSolicitarCambio =
		esTurnoJugador &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 0);
	const puedeCambiarCartas =
		esTurnoJugador &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 1);
	const puedeElegirComodin =
		esTurnoJugador &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 2);

	const esFinMano = Boolean(mano?.ganador);
	const esUltimaMano = Boolean(mano?.mano_num && partida?.longitud && mano.mano_num >= partida.longitud);

	const partidaFinalizada = Boolean(partida?.partida_finalizada);
	const resumenFinalIncompleto = Boolean(
		partidaFinalizada && (
			!datosFinalPartida ||
			typeof datosFinalPartida !== "object" ||
			!("puntos_ganados_por_kills" in datosFinalPartida) ||
			!("puntos_perdidos_por_deaths" in datosFinalPartida) ||
			!("puntuacion_ganada_por_jugadores" in datosFinalPartida)
		),
	);

	const mostrarBotonRetirada = 
		Boolean(rondaActual && rondaActual.ronda_num >= 1 && rondaActual.ronda_num <= 3);
	const puedeRetirarseDeMano = 
		mostrarBotonRetirada && 
		esTurnoJugador &&
		!jugador?.retirado && 
		!esFinMano;

	const indicacionTuTurno = 
		esTurnoJugador;

	const indicacionTurnoAjeno =
		!esTurnoJugador;

	const indicacionQuererCambiar =
		esTurnoJugador &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 0);
	
	const indicacionCambiarCartas =
		esTurnoJugador &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 1);
	
	const indicacionElegirComodin =
		esTurnoJugador &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 2);
	
	const indicacionJugarCarta =
		esTurnoJugador &&
		Boolean(rondaActual && rondaActual.ronda_num >= 1 && rondaActual.ronda_num <= 3);

	const claveEstadoTurnoActual = `${mano?.mano_id ?? "sin-mano"}-${rondaActual?.ronda_id ?? "sin-ronda"}-${rondaActual?.ronda_num ?? "x"}-${rondaActual?.cambios ?? "x"}-${partida?.turno_actual ?? "sin-turno"}`;

	const loadMesa = useCallback(async ({ showLoading = true, guardarMesaInicial = false } = {}) => {
		if (showLoading) {
			setLoading(true);
			setError("");
		}

		try {
			const res = await fetch(`/api/partida/${partidaId}/mano/mesa/`, {
				method: "GET",
				credentials: "include",
			});

			const data = await res.json().catch(() => ({}));

			if (!res.ok) {
				throw new Error(data?.detail || "No se pudo cargar la mesa");
			}

			setMesa(data);
			if (guardarMesaInicial) {
				setMesaInicial((mesaActualInicial) => mesaActualInicial ?? data);
			}

			return data;
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error cargando la mesa");
			setMesa(null);
			if (guardarMesaInicial) {
				setMesaInicial(null);
			}

			return null;
		} finally {
			if (showLoading) {
				setLoading(false);
			}
		}
	}, [partidaId]);

	useEffect(() => {
		setMesaInicial(null);
		resumenFinalSolicitadoRef.current = false;
		void loadMesa({ showLoading: true, guardarMesaInicial: true });
	}, [partidaId]);

	useEffect(() => {
		if (!puedeCambiarCartas) {
			setCartasSeleccionadas([]);
		}
	}, [puedeCambiarCartas]);

	useEffect(() => {
		if (!puedeElegirComodin) {
			setCartaComodinSeleccionada(null);
		}
	}, [puedeElegirComodin]);

	useEffect(() => {
		if (!esTurnoJugador || partidaFinalizada || esFinMano || !rondaActual) {
			setCuentaAtrasTurno(null);
			return;
		}

		const tiempoMaxTurno = Number(partida?.tiempo_max_turno ?? 0);
		if (tiempoMaxTurno <= 0) {
			setCuentaAtrasTurno(0);
			return;
		}

		if (accionAutomaticaTurnoClaveRef.current !== claveEstadoTurnoActual) {
			accionAutomaticaTurnoClaveRef.current = claveEstadoTurnoActual;
			accionAutomaticaTurnoEjecutadaRef.current = null;
			accionAutomaticaTurnoEnCursoRef.current = false;
			setCuentaAtrasTurno(tiempoMaxTurno);
		}
	}, [claveEstadoTurnoActual, esFinMano, esTurnoJugador, partida?.tiempo_max_turno, partidaFinalizada, rondaActual]);

	useEffect(() => {
		if (cuentaAtrasTurno === null || cuentaAtrasTurno <= 0) {
			return;
		}

		const timeoutId = window.setTimeout(() => {
			setCuentaAtrasTurno((valorActual) => {
				if (valorActual === null) {
					return valorActual;
				}

				return Math.max(valorActual - 1, 0);
			});
		}, 1000);

		return () => window.clearTimeout(timeoutId);
	}, [cuentaAtrasTurno]);

	useEffect(() => {
		if (cuentaAtrasTurno !== 0 || !esTurnoJugador || !rondaActual || partidaFinalizada || esFinMano) {
			return;
		}

		if (
			accionAutomaticaTurnoEnCursoRef.current ||
			accionAutomaticaTurnoEjecutadaRef.current === claveEstadoTurnoActual
		) {
			return;
		}

		accionAutomaticaTurnoEnCursoRef.current = true;
		accionAutomaticaTurnoEjecutadaRef.current = claveEstadoTurnoActual;

		void (async () => {
			try {
				if (rondaActual.ronda_num === 0 && rondaActual.cambios === 0) {
					await handleEleccionCambio(partidaId, "quiero-cambio", loadMesa);
					return;
				}

				if (rondaActual.ronda_num === 0 && rondaActual.cambios === 1) {
					const primeraCarta = Array.isArray(jugador?.cartas) && jugador.cartas.length > 0
						? jugador.cartas[0]
						: null;

					if (primeraCarta) {
						await handleCambiarCartas(partidaId, [primeraCarta], loadMesa, setCartasSeleccionadas);
					}

					return;
				}

				if (rondaActual.ronda_num === 0 && rondaActual.cambios === 2) {
					const primeraCarta = Array.isArray(jugador?.cartas) && jugador.cartas.length > 0
						? jugador.cartas[0]
						: null;

					if (primeraCarta) {
						await handleEleccionComodin(partidaId, primeraCarta, loadMesa);
					}

					return;
				}

				if (rondaActual.ronda_num > 0) {
					await handleRetirarseDeMano(partidaId, loadMesa);
				}
			} finally {
				accionAutomaticaTurnoEnCursoRef.current = false;
				setCuentaAtrasTurno(null);
			}
		})();
	}, [claveEstadoTurnoActual, cuentaAtrasTurno, esFinMano, esTurnoJugador, jugador?.cartas, loadMesa, partidaFinalizada, partidaId, rondaActual]);

	useEffect(() => {
		finManoProgramadaRef.current = null;
		resumenManoSolicitadoRef.current = null;
		setResumenMano(null);
		setCargandoResumenMano(false);
		setErrorResumenMano("");
		setCuentaAtrasFinMano(null);
		setCuentaAtrasTurno(null);
	}, [mano?.mano_id]);

	useEffect(() => {
		if (!mano?.mano_id) {
			setDatosFinalPartida(null);
		}
	}, [mano?.mano_id]);

	useEffect(() => {
		if (!resumenFinalIncompleto || resumenFinalSolicitadoRef.current) {
			return;
		}

		resumenFinalSolicitadoRef.current = true;

		void (async () => {
			try {
				const csrfToken = await obtenerCsrfToken();
				const res = await fetch(`/api/partida/${partidaId}/finalizar/`, {
					method: "PUT",
					credentials: "include",
					headers: {
						"Content-Type": "application/json",
						"X-CSRFToken": csrfToken,
					},
				});

				const data = await res.json().catch(() => null);
				if (res.ok && data) {
					setDatosFinalPartida(data);
				}
			} catch (e) {
				console.error("No se pudo recuperar el resumen final de la partida", e);
			}
		})();
	}, [partidaId, resumenFinalIncompleto]);

	useEffect(() => {
		if (manoFinalizadaId == null) {
			return;
		}

		if (finManoProgramadaRef.current === manoFinalizadaId) {
			return;
		}

		finManoProgramadaRef.current = manoFinalizadaId;
		setCuentaAtrasFinMano(10);
	}, [manoFinalizadaId]);

	useEffect(() => {
		if (cuentaAtrasFinMano === null || !esFinMano || !mano?.mano_id) {
			return;
		}

		if (resumenManoSolicitadoRef.current === mano.mano_id) {
			return;
		}

		resumenManoSolicitadoRef.current = mano.mano_id;
		setCargandoResumenMano(true);
		setErrorResumenMano("");

		void (async () => {
			try {
				const res = await fetch(`/api/partida/${partidaId}/mano/resumen/`, {
					method: "GET",
					credentials: "include",
				});

				const data = await res.json().catch(() => ({}));
				if (!res.ok) {
					throw new Error(data?.detail || "No se pudo cargar el resumen de la mano");
				}

				setResumenMano(data);
			} catch (e) {
				setErrorResumenMano(e instanceof Error ? e.message : "No se pudo cargar el resumen de la mano");
				setResumenMano(null);
			} finally {
				setCargandoResumenMano(false);
			}
		})();
	}, [cuentaAtrasFinMano, esFinMano, mano?.mano_id, partidaId]);

	useEffect(() => {
		if (cuentaAtrasFinMano === null) {
			return;
		}

		if (cuentaAtrasFinMano === 0) {
			finManoProgramadaRef.current = null;
			setCuentaAtrasFinMano(null);
			return () => undefined;
		}

		const timeoutId = window.setTimeout(() => {
			setCuentaAtrasFinMano((valorActual) => (valorActual === null ? valorActual : Math.max(valorActual - 1, 0)));
		}, 1000);

		return () => window.clearTimeout(timeoutId);
	}, [cuentaAtrasFinMano]);

	useEffect(() => {
		const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
		let socket;
		let reconnectTimer;
		let shouldReconnect = true;

		const connect = () => {
			socket = new WebSocket(`${protocol}//${window.location.host}/ws/partidas/${partidaId}/mesa/`);

			socket.onopen = () => {
				console.log("WS conectado");
			};

			socket.onmessage = async (event) => {
				const data = JSON.parse(event.data);

				if (data.type === "mano_finalizada") {
						if (data.mano_id != null) {
							setManoFinalizadaId(data.mano_id);
						}

						await loadMesa({ showLoading: false });

					return;
				}

				if (data.type === "partida_finalizada") {
					setDatosFinalPartida(data.datos_final_partida ?? null);
					finManoProgramadaRef.current = null;
					resumenManoSolicitadoRef.current = null;
					setResumenMano(null);
					setCargandoResumenMano(false);
					setErrorResumenMano("");
					setCuentaAtrasFinMano(null);
					setCuentaAtrasTurno(null);
					await loadMesa({ showLoading: false });
					return;
				}

				if (data.type === "mesa_updated") {
					await loadMesa({ showLoading: false });
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

	return (
		<div className="juego-container">
			{loading ? (
				<p>Cargando mesa...</p>
			) : error ? (
				<p role="alert">{error}</p>
			) : (
				<>
					<div className="juego-mesa">
						<InfoSuperior
							partida={partida}
							mano={mano}
							jugador={jugador}
						/>
						{mesaInicial && (
							<MesaInicialContrincantes
								partida={mesaInicial.partida}
								jugador={jugador}
								contrincantes={contrincantes}
								rondas={rondas}
								partidaId={partidaId}
							/>
						)}

						<div className="juego-mesa__cartas-y-acciones">
							{/* Contenedor lateral izquierdo: ticket del jugador */}
							<div className="juego-mesa__lado-izquierdo">
								<TicketJugador ticket={jugador?.ticket} ticket_usable={jugador?.ticket_usable} ronda_actual={rondaActual.num} cambios={rondaActual.cambios} es_turno_actual={esTurnoJugador} partidaId={partidaId} loadMesa={loadMesa} />
							</div>
							{jugador ? (
								<div className="juego-mesa__cartas-jugador-propio">
									<CartasEnMesa participante={jugador} rondas={rondas} className="cartas-en-mesa--jugador-propio" partidaId={partidaId} esJugadorPropio />
								</div>
							) : null}

							<div className="juego-mesa__cartas">
								<CartasPropias
									cartas={jugador?.cartas}
									seleccionable={puedeCambiarCartas || puedeElegirComodin || puedeJugarCarta}
									cartasSeleccionadas={puedeCambiarCartas ? cartasSeleccionadas : cartaComodinSeleccionada ? [cartaComodinSeleccionada] : []}
									partidaId={partidaId}
									onToggleCarta={async (carta) => {
										if (puedeCambiarCartas) {
											handleToggleCartaSeleccionada(puedeCambiarCartas, setCartasSeleccionadas, carta);
											return;
										}

										if (puedeElegirComodin) {
											handleToggleCartaSeleccionadaUnica(puedeElegirComodin, setCartaComodinSeleccionada, carta);
											return;
										}

										if (puedeJugarCarta) {
											await handleJugarCarta(partidaId, carta, loadMesa);
										}
									}}
								/>

								<div className="recuadro-indicaciones">
									{indicacionTuTurno ? (
										<span className="texto-indicaciones">Es tu turno.</span>
									) : indicacionTurnoAjeno ? (
										<span className="texto-indicaciones">
											Es el turno del jugador{" "}
											<span className="texto-indicaciones" style={{ color: COLORJUGADOR[partida?.turno_actual] }}>
												{partida?.turno_actual}
											</span>.
										</span>
									) : null}
									{indicacionQuererCambiar ? (
										<p className="texto-indicaciones">¡Di si quieres cambiar cartas!</p>
									) : indicacionCambiarCartas ? (
										<p className="texto-indicaciones">¡Elige las cartas que quieres cambiar!</p>
									) : indicacionElegirComodin ? (
										<p className="texto-indicaciones">¡Elige que carta quieres usar como comodín!</p>
									) : indicacionJugarCarta ? (
										<p className="texto-indicaciones">¡Elige la carta que quieres lanzar!</p>
									) : null}
									{indicacionTuTurno && cuentaAtrasTurno !== null ? (
										<p className="texto-indicaciones">Tienes {cuentaAtrasTurno} s.</p>
									) : null}
								</div>
							</div>

							{puedeCambiarCartas ? (
								<div className="juego-mesa__acciones-cambio" aria-label="Acciones de cambio">
									<button
										type="button"
										className="main-primary-button"
										onClick={() => void handleCambiarCartas(partidaId, cartasSeleccionadas, loadMesa, setCartasSeleccionadas)}
									>
										Cambiar cartas
									</button>
								</div>
							) : puedeSolicitarCambio ? (
								<div className="juego-mesa__acciones-cambio" aria-label="Acciones de cambio">
									<button
										type="button"
										className="main-primary-button"
										onClick={() => void handleEleccionCambio(partidaId, "quiero-cambio", loadMesa)}
									>
										Quiero cambio
									</button>
									<button
										type="button"
										className="main-primary-button"
										onClick={() => void handleEleccionCambio(partidaId, "no-quiero-cambio", loadMesa)}
									>
										No quiero cambio
									</button>
								</div>
							) : puedeElegirComodin ? (
								<div className="juego-mesa__acciones-cambio" aria-label="Acciones de cambio">
									<button
										type="button"
										className="main-primary-button"
										disabled={!cartaComodinSeleccionada}
										onClick={() => void handleEleccionComodin(partidaId, cartaComodinSeleccionada, loadMesa)}
									>
										Elegir carta comodín
									</button>
								</div>
							) : mostrarBotonRetirada ? (
								<div className="juego-mesa__acciones-cambio" aria-label="Acciones de cambio">
									<button
										type="button"
										className="main-primary-button"
										disabled={!puedeRetirarseDeMano}
										onClick={() => void handleRetirarseDeMano(partidaId, loadMesa)}
									>
										Retirarse de la mano
									</button>
								</div>
							) : null}
						</div>
					</div>
					{cuentaAtrasFinMano !== null ? (
						<div className="juego-resumen-mano-centro" role="presentation">
							<div className="form-card juego-resumen-mano-centro__card">
								<ResumenManoPanel
									cuentaAtras={cuentaAtrasFinMano}
									ganador={mano?.ganador}
									resumenMano={resumenMano}
									cargandoResumen={cargandoResumenMano}
									errorResumen={errorResumenMano}
									esUltimaMano={esUltimaMano}
								/>
							</div>
						</div>
					) : null}
					{partidaFinalizada ? (
						<ResumenPartidaOverlay
							datosFinalPartida={datosFinalPartida}
						/>
					) : null}
				</>
			)}
		</div>
	);
}