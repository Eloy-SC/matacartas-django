import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import CartasPropias from "./CartasPropias.jsx";
import {
	formatCartas,
	handleCambiarCartas,
	handleEleccionCambio,
	handleEleccionComodin,
	handleJugarCarta,
	handleSiguienteMano,
	handleToggleCartaSeleccionada,
	handleToggleCartaSeleccionadaUnica,
} from "./FuncionesMesa.jsx";
import CartasEnMesa from "./CartasEnMesa.jsx";
import InfoSuperior from "./InfoSuperior.jsx";
import MesaInicialContrincantes from "./MesaInicialContrincantes.jsx";
import "../../styles/mesa.css";

const COLORJUGADOR = {
    rojo: "red",
    naranja: "orange",
    amarillo: "yellow",
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
	const [cuentaAtrasFinMano, setCuentaAtrasFinMano] = useState(null);
	const [manoFinalizadaId, setManoFinalizadaId] = useState(null);
	const finManoProgramadaRef = useRef(null);
	const siguienteManoSolicitadaRef = useRef(null);
	const esJugadorPosicionCeroRef = useRef(false);

	const partida = mesa?.partida ?? null;
	const mano = mesa?.mano ?? null;
	const jugador = mesa?.jugador ?? null;
	const contrincantes = mesa?.contrincantes ?? [];
	const rondas = mesa?.rondas ?? [];
	const rondaActual = rondas[rondas.length - 1] ?? null;
	const esJugadorPosicionCero = partida?.disposicion_jugadores?.[0] === jugador?.color;
	const rondaCambio = rondas.length === 1 ? rondas[0] : null;
	const puedeJugarCarta =
		Boolean(partida?.turno_actual && jugador?.color && partida.turno_actual === jugador.color) &&
		Boolean(rondaActual && rondaActual.ronda_num >= 1 && rondaActual.ronda_num <= 3);
	const puedeSolicitarCambio =
		Boolean(partida?.turno_actual && jugador?.color && partida.turno_actual === jugador.color) &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 0);
	const puedeCambiarCartas =
		Boolean(partida?.turno_actual && jugador?.color && partida.turno_actual === jugador.color) &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 1);
	const puedeElegirComodin =
		Boolean(partida?.turno_actual && jugador?.color && partida.turno_actual === jugador.color) &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 2);

	const indicacionTuTurno = 
		Boolean(partida?.turno_actual && jugador?.color && partida.turno_actual === jugador.color);

	const indicacionTurnoAjeno =
		Boolean(partida?.turno_actual && jugador?.color && partida.turno_actual !== jugador.color);

	const indicacionQuererCambiar =
		Boolean(partida?.turno_actual && jugador?.color && partida.turno_actual === jugador.color) &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 0);
	
	const indicacionCambiarCartas =
		Boolean(partida?.turno_actual && jugador?.color && partida.turno_actual === jugador.color) &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 1);
	
	const indicacionElegirComodin =
		Boolean(partida?.turno_actual && jugador?.color && partida.turno_actual === jugador.color) &&
		Boolean(rondaCambio && rondaCambio.ronda_num === 0 && rondaCambio.cambios === 2);
	
	const indicacionJugarCarta =
		Boolean(partida?.turno_actual && jugador?.color && partida.turno_actual === jugador.color) &&
		Boolean(rondaActual && rondaActual.ronda_num >= 1 && rondaActual.ronda_num <= 3);

	useEffect(() => {
		esJugadorPosicionCeroRef.current = esJugadorPosicionCero;
	}, [esJugadorPosicionCero]);

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
		finManoProgramadaRef.current = null;
		setCuentaAtrasFinMano(null);
	}, [mano?.mano_id]);

	useEffect(() => {
		if (manoFinalizadaId == null) {
			return;
		}

		if (finManoProgramadaRef.current === manoFinalizadaId) {
			return;
		}

		finManoProgramadaRef.current = manoFinalizadaId;
		setCuentaAtrasFinMano(7);
	}, [manoFinalizadaId]);

	useEffect(() => {
		if (cuentaAtrasFinMano === null) {
			return;
		}

		if (cuentaAtrasFinMano === 0) {
			if (mano?.mano_id == null || siguienteManoSolicitadaRef.current === mano.mano_id) {
				return () => undefined;
			}

			siguienteManoSolicitadaRef.current = mano.mano_id;
			let cancelado = false;

			void (async () => {
				try {
					await handleSiguienteMano(partidaId, loadMesa);
				} finally {
					if (!cancelado) {
						finManoProgramadaRef.current = null;
						setCuentaAtrasFinMano(null);
					}
				}
			})();

			return () => {
				cancelado = true;
			};
		}

		const timeoutId = window.setTimeout(() => {
			setCuentaAtrasFinMano((valorActual) => (valorActual === null ? valorActual : Math.max(valorActual - 1, 0)));
		}, 1000);

		return () => window.clearTimeout(timeoutId);
	}, [cuentaAtrasFinMano, loadMesa, partidaId]);

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
						if (data.mano_id != null && siguienteManoSolicitadaRef.current !== data.mano_id) {
							setManoFinalizadaId(data.mano_id);
						}

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
								{cuentaAtrasFinMano !== null ? (
									<p className="texto-indicaciones">Nueva mano en {cuentaAtrasFinMano} s.</p>
								) : (
									<>
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
									</>
								)}
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
						) : null}
					</div>
				</div>
			)}
		</div>
	);
}