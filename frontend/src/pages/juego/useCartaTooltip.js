import { useState } from "react";
import { CARTAS_A_RENDERIZAR } from "./DiccionarioCartasFront.js";

export function obtenerNombreVisibleCarta(cartaId, datos) {
	const clave = typeof cartaId === "string" ? cartaId.trim().toUpperCase() : "";
	const entrada = CARTAS_A_RENDERIZAR[clave];

	if (datos?.nombre && entrada?.nombre) {
		return entrada.nombre;
	}

	return datos?.nombre || entrada?.nombre || cartaId;
}

export function useCartaTooltip(partidaId) {
	const [detalleCarta, setDetalleCarta] = useState(null);
	const [detalleLoading, setDetalleLoading] = useState(false);
	const [detalleError, setDetalleError] = useState("");
	const [tooltipPosition, setTooltipPosition] = useState(null);

	const manejarHoverCarta = async (carta, evento) => {
		if (!partidaId || !carta) {
			return;
		}

		const rectangulo = evento?.currentTarget?.getBoundingClientRect?.();
		setTooltipPosition(rectangulo ? {
			left: rectangulo.left,
			top: rectangulo.top,
			width: rectangulo.width,
			height: rectangulo.height,
		} : null);

		setDetalleLoading(true);
		setDetalleError("");
		setDetalleCarta({ carta, nombreMostrar: obtenerNombreVisibleCarta(carta, null) });

		try {
			const respuesta = await fetch(`/api/partida/${partidaId}/mano/datos-carta/?carta=${encodeURIComponent(carta)}`, {
				method: "GET",
				credentials: "include",
			});
			const datos = await respuesta.json().catch(() => ({}));

			if (!respuesta.ok) {
				throw new Error(datos?.detail || "No se pudieron cargar los datos de la carta");
			}

			setDetalleCarta({
				carta,
				nombreMostrar: obtenerNombreVisibleCarta(carta, datos),
				tipo: datos?.tipo ?? "-",
				fuerza: datos?.fuerza ?? "-",
				riqueza: datos?.riqueza ?? "-",
			});
		} catch (error) {
			setDetalleError(error instanceof Error ? error.message : "No se pudieron cargar los datos de la carta");
			setDetalleCarta({
				carta,
				nombreMostrar: obtenerNombreVisibleCarta(carta, null),
			});
		} finally {
			setDetalleLoading(false);
		}
	};

	const limpiarHoverCarta = () => {
		setDetalleCarta(null);
		setDetalleLoading(false);
		setDetalleError("");
		setTooltipPosition(null);
	};

	return {
		detalleCarta,
		detalleLoading,
		detalleError,
		tooltipPosition,
		manejarHoverCarta,
		limpiarHoverCarta,
	};
}