import { createPortal } from "react-dom";
import { useNavigate } from "react-router-dom";

const COLORJUGADOR = {
    rojo: "red",
    naranja: "orange",
    amarillo: "goldenrod",
    verde: "green",
    azul: "blue",
    morado: "purple",
}

function formatearPosiciones(posiciones) {
	if (!posiciones || typeof posiciones !== "object") {
		return [];
	}

	return Object.entries(posiciones)
		.filter(([, jugadores]) => Array.isArray(jugadores) && jugadores.length > 0)
		.map(([posicion, jugadores]) => ({
			posicion,
			jugadores,
		}));
}

export default function ResumenPartidaOverlay({ datosFinalPartida }) {
	const navigate = useNavigate();

	if (!datosFinalPartida || typeof document === "undefined") {
		return null;
	}

	const puntosGanadosPorKills = datosFinalPartida.puntos_ganados_por_kills ?? {};
	const puntosPerdidosPorDeaths = datosFinalPartida.puntos_perdidos_por_deaths ?? {};
	const posiciones = formatearPosiciones(datosFinalPartida.posiciones);
	const puntosGanadosPorJugadores = datosFinalPartida.puntuacion_ganada_por_jugadores ?? {};

	return createPortal(
		<div className="juego-resumen-overlay" role="presentation">
			<div className="juego-resumen-overlay__backdrop" />
			<div className="form-card juego-resumen-overlay__card" role="dialog" aria-modal="true" aria-labelledby="resumen-partida-title">
				<h2 id="resumen-partida-title" className="juego-resumen-overlay__title">PARTIDA FINALIZADA</h2>

				<div className="juego-resumen-overlay__section">
					<h3 className="juego-resumen-overlay__subtitle">Puntos ganados por matar cartas</h3>
					<div className="juego-resumen-overlay__kv-list">
						{Object.entries(puntosGanadosPorKills).map(([color, puntos]) => (
							<div key={color} className="juego-resumen-overlay__kv-row">
								<span className="juego-resumen-overlay__value">El jugador </span>
								<span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[color] }}>
									{color}
								</span>
								<span className="juego-resumen-overlay__value"> ha ganado {puntos} puntos.</span>
							</div>
						))}
					</div>
				</div>

				<div className="juego-resumen-overlay__section">
					<h3 className="juego-resumen-overlay__subtitle">Puntos perdidos por muertes de cartas</h3>
					<div className="juego-resumen-overlay__kv-list">
						{Object.entries(puntosPerdidosPorDeaths).map(([color, puntos]) => (
							<div key={color} className="juego-resumen-overlay__kv-row">
								<span className="juego-resumen-overlay__value">El jugador </span>
								<span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[color] }}>
									{color}
								</span>
								<span className="juego-resumen-overlay__value"> ha perdido {puntos} puntos.</span>
							</div>
						))}
					</div>
				</div>

				{datosFinalPartida.jug_as_extranjero ? (
					<div className="juego-resumen-overlay__section">
						<h3 className="juego-resumen-overlay__subtitle">As extranjero</h3>
						<div className="juego-resumen-overlay__kv-list">
							<div className="juego-resumen-overlay__kv-row">
								<span className="juego-resumen-overlay__label">El jugador </span>
								<span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[datosFinalPartida.jug_as_extranjero] }}>
									{datosFinalPartida.jug_as_extranjero}
								</span>
							</div>
							<div className="juego-resumen-overlay__kv-row">
								<span className="juego-resumen-overlay__label">Puntos extra</span>
								<span className="juego-resumen-overlay__value">{datosFinalPartida.puntuacion_extra_jug_as_extranjero ?? 0}</span>
							</div>
						</div>
					</div>
				) : null}

				<div className="juego-resumen-overlay__section">
					<h3 className="juego-resumen-overlay__subtitle">Posiciones finales</h3>
					<div className="juego-resumen-overlay__positions">
						{posiciones.map(({ posicion, jugadores }) => (
							<div key={posicion} className="juego-resumen-overlay__position-block">
								<p className="juego-resumen-overlay__position-title">Posición {posicion}</p>
								{jugadores.map((jugador) => {
									const colorJugador = typeof jugador?.color === "string" ? jugador.color.toLowerCase() : "";
									const puntosGanadosPartida = colorJugador
										? (puntosGanadosPorJugadores[colorJugador] ?? puntosGanadosPorJugadores[jugador.color])
										: undefined;

									return (
										<div key={`${posicion}-${jugador.color ?? jugador.nombre}`} className="juego-resumen-overlay__player-data">
											<p>
												{jugador.nombre ?? jugador.color ?? "Jugador"} (<span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[jugador.color] }}>{jugador.color ?? "desconocido"}</span>)
											</p>
											<p>{jugador.puntos ?? 0} puntos en partida</p>
											{puntosGanadosPartida !== undefined ? (
												<p style={{ fontWeight: "bold" }}>Puntuación ganada: {puntosGanadosPartida}</p>
											) : 
											<p style={{ fontWeight: "bold" }}>No se ha ganado puntuación en esta partida</p>
											}
										</div>
									);
								})}
							</div>
						))}
					</div>
				</div>

				<div className="juego-resumen-overlay__actions">
					<button type="button" className="main-primary-button" onClick={() => navigate("/inicio")}>Ir a inicio</button>
				</div>
			</div>
		</div>,
		document.body,
	);
}