import "../../styles/cartas_propias.css";
import CartaTooltipFlotante from "./CartaTooltipFlotante.jsx";
import { renderizarCarta } from "./RenderizadoCartas.jsx";
import { useCartaTooltip } from "./useCartaTooltip.js";

export default function CartasPropias({
	cartas = [],
	seleccionable = false,
	cartasSeleccionadas = [],
	onToggleCarta,
	partidaId,
}) {
	const {
		detalleCarta,
		detalleLoading,
		detalleError,
		tooltipPosition,
		manejarHoverCarta,
		limpiarHoverCarta,
	} = useCartaTooltip(partidaId);
	const cartasVisibles = Array.isArray(cartas) ? cartas : [];
	const cartasSeleccionadasVisibles = Array.isArray(cartasSeleccionadas) ? cartasSeleccionadas : [];
	const puedeSeleccionar = seleccionable && typeof onToggleCarta === "function";
	const cartaTooltipVisible = detalleCarta?.carta && cartasVisibles.includes(detalleCarta.carta);

	return (
		<section className="cartas-propias" aria-label="Cartas del jugador">
			{cartasVisibles.length === 0 ? (
				<p className="cartas-propias__vacio">No hay ninguna carta en tu mano.</p>
			) : (
				<div className="cartas-propias__contenedor" role="list">
					{cartasVisibles.map((carta, index) =>
						renderizarCarta({
							carta,
							index,
							seleccionable: puedeSeleccionar,
							seleccionada: cartasSeleccionadasVisibles.includes(carta),
							onToggleCarta,
							onMouseEnter: (evento) => void manejarHoverCarta(carta, evento),
							onMouseLeave: limpiarHoverCarta,
						})
					)}
				</div>
			)}
			{cartaTooltipVisible ? (
				<CartaTooltipFlotante
					carta={detalleCarta?.carta}
					detalleCarta={detalleCarta}
					detalleLoading={detalleLoading}
					detalleError={detalleError}
					tooltipPosition={tooltipPosition}
				/>
			) : null}
		</section>
	);
}