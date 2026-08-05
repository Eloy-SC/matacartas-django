import cartaBocaAbajo from "../../assets/cartas/carta_boca_abajo.png";
import "../../styles/cartas_propias.css";
import CartaTooltipFlotante from "./CartaTooltipFlotante.jsx";
import { describirCarta, obtenerRutaCarta } from "./RenderizadoCartas.jsx";
import { useCartaTooltip } from "./useCartaTooltip.js";

const ANCHO_CARTA = 120;
const ALTO_CARTA = 180;
const DESPLAZAMIENTO_CARTAS = 26;

function obtenerCartasJugadasDeParticipante(rondas, colorParticipante) {
	if (!Array.isArray(rondas) || !colorParticipante) {
		return [];
	}

	return [...rondas]
		.filter((ronda) => {
			const numRonda = ronda?.ronda_num ?? 0;

			return numRonda > 0 && numRonda < 4;
		})
		.sort((rondaA, rondaB) => (rondaA?.ronda_num ?? 0) - (rondaB?.ronda_num ?? 0))
		.flatMap((ronda) => {
			const cartaJugada = ronda?.cartas?.[colorParticipante];

			if (Array.isArray(cartaJugada)) {
				return cartaJugada.filter(Boolean);
			}

			if (typeof cartaJugada === "string" && cartaJugada.trim()) {
				return [cartaJugada];
			}

			return [];
		});
}

function obtenerCartaReveladaDeRonda(ronda, colorParticipante) {
	if ((ronda?.ronda_num ?? 0) !== 4 || !colorParticipante) {
		return null;
	}

	const cartaRevelada = ronda?.cartas?.[colorParticipante];

	if (Array.isArray(cartaRevelada)) {
		return cartaRevelada.find(Boolean) ?? null;
	}

	if (typeof cartaRevelada === "string" && cartaRevelada.trim()) {
		return cartaRevelada;
	}

	return null;
}

function tieneComodinSeleccionado(participante) {
	if (typeof participante?.carta_comodin === "string") {
		return participante.carta_comodin.trim().length > 0;
	}

	return Boolean(participante?.carta_comodin);
}

function obtenerCartaComodinJugadorPropio(participante, esJugadorPropio) {
	if (!esJugadorPropio) {
		return null;
	}

	if (typeof participante?.carta_comodin === "string" && participante.carta_comodin.trim()) {
		return participante.carta_comodin;
	}

	return null;
}

function renderizarCartaConTooltip({ carta, indice, manejarHoverCarta, limpiarHoverCarta }) {
	const rutaCarta = obtenerRutaCarta(carta);

	if (!rutaCarta) {
		return null;
	}

	return (
		<div
			key={`${carta}-${indice}`}
			className="cartas-en-mesa__carta-wrapper"
			style={{
				position: "absolute",
				left: 0,
				top: `${indice * DESPLAZAMIENTO_CARTAS}px`,
				width: `${ANCHO_CARTA}px`,
				height: `${ALTO_CARTA}px`,
				zIndex: indice + 1,
			}}
			onMouseEnter={(evento) => void manejarHoverCarta(carta, evento)}
			onMouseLeave={limpiarHoverCarta}
			role="listitem"
		>
			<img
				className="cartas-en-mesa__carta-jugada"
				src={rutaCarta}
				alt={describirCarta(carta)}
			/>
		</div>
	);
}

function renderizarCartaCompacta({ carta, manejarHoverCarta, limpiarHoverCarta }) {
	const rutaCarta = obtenerRutaCarta(carta);

	if (!rutaCarta) {
		return null;
	}

	return (
		<div
			className="cartas-en-mesa__carta-wrapper"
			style={{ position: "relative" }}
			onMouseEnter={(evento) => void manejarHoverCarta(carta, evento)}
			onMouseLeave={limpiarHoverCarta}
			role="listitem"
		>
			<img
				className="cartas-en-mesa__carta-jugada"
				src={rutaCarta}
				alt={describirCarta(carta)}
			/>
		</div>
	);
}

export default function CartasEnMesa({ participante, rondas = [], className = "", partidaId, esJugadorPropio = false }) {
	const {
		detalleCarta,
		detalleLoading,
		detalleError,
		tooltipPosition,
		manejarHoverCarta,
		limpiarHoverCarta,
	} = useCartaTooltip(partidaId);
	const rondaActual = Array.isArray(rondas) && rondas.length > 0 ? rondas[rondas.length - 1] : null;
	const cartasJugadas = obtenerCartasJugadasDeParticipante(rondas, participante?.color);
	const cartaRevelada = obtenerCartaReveladaDeRonda(rondaActual, participante?.color);
	const conComodin = tieneComodinSeleccionado(participante);
	const cartaComodinJugadorPropio = obtenerCartaComodinJugadorPropio(participante, esJugadorPropio);
	const alturaPila = cartasJugadas.length > 0 ? ALTO_CARTA + (cartasJugadas.length - 1) * DESPLAZAMIENTO_CARTAS : 0;

	return (
		<div className={`cartas-en-mesa ${className}`.trim()}>
			{cartaRevelada ? (
				renderizarCartaCompacta({
					carta: cartaRevelada,
					manejarHoverCarta,
					limpiarHoverCarta,
				})
			) : cartaComodinJugadorPropio ? (
				<div
					className="cartas-en-mesa__carta-wrapper"
					style={{ position: "relative" }}
					onMouseEnter={(evento) => void manejarHoverCarta(cartaComodinJugadorPropio, evento)}
					onMouseLeave={limpiarHoverCarta}
					role="listitem"
				>
					<img
						className="cartas-en-mesa__carta-boca-abajo"
						src={cartaBocaAbajo}
						alt="Carta comodín"
					/>
				</div>
			) : conComodin ? (
				<img className="cartas-en-mesa__carta-boca-abajo" src={cartaBocaAbajo} alt="Carta boca abajo" />
			) : null}
			<div className="cartas-en-mesa__pila" style={{ height: `${alturaPila}px` }}>
				{cartasJugadas.length === 0 ? (
					<div className="cartas-en-mesa__pila cartas-en-mesa__pila--vacia" />
				) : (
					cartasJugadas.map((carta, indice) =>
						renderizarCartaConTooltip({
							carta,
							indice,
							manejarHoverCarta,
							limpiarHoverCarta,
						})
					)
				)}
			</div>
			<CartaTooltipFlotante
				carta={detalleCarta?.carta}
				detalleCarta={detalleCarta}
				detalleLoading={detalleLoading}
				detalleError={detalleError}
				tooltipPosition={tooltipPosition}
			/>
		</div>
	);
}