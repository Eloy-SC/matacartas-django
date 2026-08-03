import "../../styles/cartas_propias.css";
import { renderizarCarta } from "./RenderizadoCartas.jsx";

export default function CartasPropias({
	cartas = [],
	seleccionable = false,
	cartasSeleccionadas = [],
	onToggleCarta,
}) {
	const cartasVisibles = Array.isArray(cartas) ? cartas : [];
	const cartasSeleccionadasVisibles = Array.isArray(cartasSeleccionadas) ? cartasSeleccionadas : [];
	const puedeSeleccionar = seleccionable && typeof onToggleCarta === "function";

	return (
		<section className="cartas-propias" aria-label="Cartas del jugador">
			{cartasVisibles.length === 0 ? (
				<p className="cartas-propias__vacio">Aún no tienes cartas repartidas.</p>
			) : (
				<div className="cartas-propias__contenedor" role="list">
					{cartasVisibles.map((carta, index) =>
						renderizarCarta({
							carta,
							index,
							seleccionable: puedeSeleccionar,
							seleccionada: cartasSeleccionadasVisibles.includes(carta),
							onToggleCarta,
						})
					)}
				</div>
			)}
		</section>
	);
}