import { useState } from "react";
import "../../styles/cartas_propias.css";
import { renderizarCarta } from "./RenderizadoCartas.jsx";
import { CARTAS_A_RENDERIZAR } from "./DiccionarioCartasFront.jsx";

export default function CartasPropias({
	cartas = [],
	seleccionable = false,
	cartasSeleccionadas = [],
	onToggleCarta,
	partidaId,
}) {
	const [detalleCarta, setDetalleCarta] = useState(null);
	const [detalleLoading, setDetalleLoading] = useState(false);
	const [detalleError, setDetalleError] = useState("");
	const cartasVisibles = Array.isArray(cartas) ? cartas : [];
	const cartasSeleccionadasVisibles = Array.isArray(cartasSeleccionadas) ? cartasSeleccionadas : [];
	const puedeSeleccionar = seleccionable && typeof onToggleCarta === "function";

	const obtenerNombreVisible = (cartaId, datos) => {
		const clave = typeof cartaId === "string" ? cartaId.trim().toUpperCase() : "";
		const entrada = CARTAS_A_RENDERIZAR[clave];
		if (datos?.nombre && entrada?.nombre) {
			return entrada.nombre;
		}
		return datos?.nombre || entrada?.nombre || cartaId;
	};

	const manejarHoverCarta = async (carta) => {
		if (!partidaId || !carta) {
			return;
		}

		setDetalleLoading(true);
		setDetalleError("");
		setDetalleCarta({ carta, nombreMostrar: obtenerNombreVisible(carta, null) });

		try {
			const respuesta = await fetch(
				`/api/partida/${partidaId}/mano/datos-carta/?carta=${encodeURIComponent(carta)}`,
				{
					method: "GET",
					credentials: "include",
				}
			);
			const datos = await respuesta.json().catch(() => ({}));

			if (!respuesta.ok) {
				throw new Error(datos?.detail || "No se pudieron cargar los datos de la carta");
			}

			setDetalleCarta({
				carta,
				nombreMostrar: obtenerNombreVisible(carta, datos),
				tipo: datos?.tipo ?? "-",
				fuerza: datos?.fuerza ?? "-",
				riqueza: datos?.riqueza ?? "-",
			});
		} catch (error) {
			setDetalleError(error instanceof Error ? error.message : "No se pudieron cargar los datos de la carta");
			setDetalleCarta({
				carta,
				nombreMostrar: obtenerNombreVisible(carta, null),
			});
		} finally {
			setDetalleLoading(false);
		}
	};

	const limpiarHoverCarta = () => {
		setDetalleCarta(null);
		setDetalleLoading(false);
		setDetalleError("");
	};

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
							onMouseEnter: () => void manejarHoverCarta(carta),
							onMouseLeave: limpiarHoverCarta,
							tooltipVisible: detalleCarta?.carta === carta,
							tooltipData: detalleCarta?.carta === carta ? detalleCarta : null,
							tooltipLoading: detalleLoading && detalleCarta?.carta === carta,
							tooltipError: detalleError && detalleCarta?.carta === carta ? detalleError : "",
						})
					)}
				</div>
			)}
		</section>
	);
}