import { createPortal } from "react-dom";
import { CARTAS_A_RENDERIZAR } from "./DiccionarioCartasFront.jsx";
import { obtenerTipoVisual } from "./RenderizadoCartas.jsx";

function obtenerEfectoCarta(carta) {
	if (typeof carta !== "string") {
		return "";
	}

	const clave = carta.trim().toUpperCase();
	return CARTAS_A_RENDERIZAR[clave]?.efecto?.trim() || "";
}

export default function CartaTooltipFlotante({ carta, detalleCarta, detalleLoading, detalleError, tooltipPosition }) {
	if (!carta || !tooltipPosition || typeof document === "undefined") {
		return null;
	}

	const tipoVisual = obtenerTipoVisual(detalleCarta?.tipo);
	const claseTipo = tipoVisual.className ? `cartas-propias__tooltip-tipo ${tipoVisual.className}` : "cartas-propias__tooltip-tipo";
	const nombreMostrar = detalleCarta?.nombreMostrar || carta;
	const efectoCarta = obtenerEfectoCarta(carta);
	const mostrarDebajo = tooltipPosition.top < 180;
	const left = tooltipPosition.left + tooltipPosition.width / 2;
	const top = mostrarDebajo ? tooltipPosition.top + tooltipPosition.height + 12 : tooltipPosition.top - 12;
	const transform = mostrarDebajo ? "translate(-50%, 0)" : "translate(-50%, -100%)";

	return createPortal(
		<div
			className="cartas-propias__tooltip"
			role="tooltip"
			style={{
				position: "fixed",
				left: `${left}px`,
				top: `${top}px`,
				right: "auto",
				bottom: "auto",
				transform,
				display: "block",
				width: "max-content",
				boxSizing: "border-box",
				zIndex: 99999,
				pointerEvents: "none",
			}}
		>
			{detalleLoading ? (
				<p className="cartas-propias__tooltip-cargando">Cargando datos…</p>
			) : detalleError ? (
				<p className="cartas-propias__tooltip-error">{detalleError}</p>
			) : (
				<>
					<p className="cartas-propias__tooltip-titulo">{nombreMostrar}</p>
					<p className={claseTipo}>{tipoVisual.label}</p>
					<p><span className="cartas-propias__tooltip-valor cartas-propias__tooltip-valor--fuerza">{detalleCarta?.fuerza ?? "?"}</span><span className="cartas-propias__tooltip-etiqueta"> de fuerza</span></p>
					<p><span className="cartas-propias__tooltip-valor cartas-propias__tooltip-valor--riqueza">{detalleCarta?.riqueza ?? "?"}</span><span className="cartas-propias__tooltip-etiqueta"> de riqueza</span></p>
					{efectoCarta ? <p className="cartas-propias__tooltip-efecto">{efectoCarta}</p> : null}
				</>
			)}
		</div>,
		document.body,
	);
}
