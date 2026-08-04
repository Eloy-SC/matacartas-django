import { CARTAS_A_RENDERIZAR, TIPOS_CARTA } from "./DiccionarioCartasFront.jsx";

const CARTAS_IMAGENES = import.meta.glob("../../assets/cartas/*.png", {
	eager: true,
	import: "default",
});

export function obtenerTipoVisual(tipo) {
	const clave = typeof tipo === "string" ? tipo.trim().toLowerCase() : "";
	const tipoDefinido = TIPOS_CARTA[clave];

	if (!tipoDefinido) {
		return { label: tipo || "-", className: "" };
	}

	return { label: tipoDefinido.label, className: tipoDefinido.className };
}

export function obtenerRutaCarta(carta) {
	if (typeof carta !== "string") {
		return null;
	}

	const clave = carta.trim().toUpperCase();
	const entrada = CARTAS_A_RENDERIZAR[clave];
	if (!entrada?.imagen) {
		return null;
	}

	const nombreArchivo = entrada.imagen;
	const coincidencia = Object.entries(CARTAS_IMAGENES).find(([ruta]) => ruta.endsWith(nombreArchivo));
	return coincidencia?.[1] ?? null;
}

export function describirCarta(carta) {
	if (typeof carta !== "string") {
		return "carta";
	}

	const coincidencia = carta.trim().toUpperCase().match(/^(\d{1,2})_([A-Z]+)$/);
	if (!coincidencia) {
		return carta.toLowerCase();
	}

	const [, numero, palo] = coincidencia;
	return `${numero} de ${palo.toLowerCase()}`;
}

export function renderizarCarta({
	carta,
	index,
	seleccionable = false,
	seleccionada = false,
	onToggleCarta,
	onMouseEnter,
	onMouseLeave,
	tooltipVisible = false,
	tooltipData = null,
	tooltipLoading = false,
	tooltipError = "",
}) {
	const rutaCarta = obtenerRutaCarta(carta);

	if (!rutaCarta) {
		return null;
	}

	const key = `${carta}-${index}`;
	const cartaDescripcion = describirCarta(carta);
	const claveCarta = typeof carta === "string" ? carta.trim().toUpperCase() : "";
	const entradaCarta = CARTAS_A_RENDERIZAR[claveCarta];
	const efectoCarta = entradaCarta?.efecto?.trim();
	const tipoVisual = obtenerTipoVisual(tooltipData?.tipo);
	const claseTipo = tipoVisual.className ? `cartas-propias__tooltip-tipo ${tipoVisual.className}` : "cartas-propias__tooltip-tipo";

	const contenidoCarta = (
		<img
			className="cartas-propias__carta"
			src={rutaCarta}
			alt={cartaDescripcion}
		/>
	);

	const cartaElement = !seleccionable || typeof onToggleCarta !== "function" ? (
		<div
			key={key}
			className="cartas-propias__carta-wrapper"
			onMouseEnter={onMouseEnter}
			onMouseLeave={onMouseLeave}
			role="listitem"
		>
			{contenidoCarta}
			{tooltipVisible ? (
				<div className="cartas-propias__tooltip" role="tooltip">
					{tooltipLoading ? (
						<p className="cartas-propias__tooltip-cargando">Cargando datos…</p>
					) : tooltipError ? (
						<p className="cartas-propias__tooltip-error">{tooltipError}</p>
					) : (
						<>
							<p className="cartas-propias__tooltip-titulo">{tooltipData?.nombreMostrar || cartaDescripcion}</p>
							<p className={claseTipo}>{tipoVisual.label}</p>
							<p><span className="cartas-propias__tooltip-valor cartas-propias__tooltip-valor--fuerza">{tooltipData?.fuerza ?? "?"}</span><span className="cartas-propias__tooltip-etiqueta"> de fuerza</span></p>
							<p><span className="cartas-propias__tooltip-valor cartas-propias__tooltip-valor--riqueza">{tooltipData?.riqueza ?? "?"}</span><span className="cartas-propias__tooltip-etiqueta"> de riqueza</span></p>
							{efectoCarta ? (
								<p className="cartas-propias__tooltip-efecto"><span className="cartas-propias__tooltip-etiqueta"></span>{efectoCarta}</p>
							) : null}
						</>
					)}
				</div>
			) : null}
		</div>
	) : (
		<div
			key={key}
			className="cartas-propias__carta-wrapper"
			onMouseEnter={onMouseEnter}
			onMouseLeave={onMouseLeave}
		>
			<button
				type="button"
				className={`cartas-propias__carta-boton${seleccionada ? " cartas-propias__carta-boton--selected" : ""}`}
				aria-pressed={seleccionada}
				onClick={() => onToggleCarta(carta)}
				role="listitem"
			>
				{contenidoCarta}
			</button>
			{tooltipVisible ? (
				<div className="cartas-propias__tooltip" role="tooltip">
					{tooltipLoading ? (
						<p className="cartas-propias__tooltip-cargando">Cargando datos…</p>
					) : tooltipError ? (
						<p className="cartas-propias__tooltip-error">{tooltipError}</p>
					) : (
						<>
							<p className="cartas-propias__tooltip-titulo">{tooltipData?.nombreMostrar || cartaDescripcion}</p>
							<p><span className="cartas-propias__tooltip-etiqueta">Tipo:</span> <span className={claseTipo}>{tipoVisual.label}</span></p>
							<p><span className="cartas-propias__tooltip-etiqueta">Fuerza:</span> <span className="cartas-propias__tooltip-valor cartas-propias__tooltip-valor--fuerza">{tooltipData?.fuerza ?? "-"}</span></p>
							<p><span className="cartas-propias__tooltip-etiqueta">Riqueza:</span> <span className="cartas-propias__tooltip-valor cartas-propias__tooltip-valor--riqueza">{tooltipData?.riqueza ?? "-"}</span></p>
							{efectoCarta ? (
								<p className="cartas-propias__tooltip-efecto"><span className="cartas-propias__tooltip-etiqueta">Efecto:</span> {efectoCarta}</p>
							) : null}
						</>
					)}
				</div>
			) : null}
		</div>
	);

	return cartaElement;
}