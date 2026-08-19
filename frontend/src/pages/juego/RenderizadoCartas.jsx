import { CARTAS_A_RENDERIZAR, TIPOS_CARTA } from "./DiccionarioCartasFront.js";

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
}) {
	const rutaCarta = obtenerRutaCarta(carta);

	if (!rutaCarta) {
		return null;
	}

	const key = `${carta}-${index}`;
	const cartaDescripcion = describirCarta(carta);

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
		</div>
	);

	return cartaElement;
}