import "../../styles/cartas_propias.css";

const CARTAS_IMAGENES = import.meta.glob("../../assets/cartas/*.png", {
	eager: true,
	import: "default",
});

function normalizarNombreCarta(carta) {
	if (typeof carta !== "string") {
		return "";
	}

	const coincidencia = carta.trim().toUpperCase().match(/^(\d{1,2})_([A-Z]+)$/);
	if (!coincidencia) {
		return "";
	}

	const [, numero, palo] = coincidencia;
	return `carta_${palo.toLowerCase()}_${numero}.png`;
}

function obtenerRutaCarta(carta) {
	const nombreArchivo = normalizarNombreCarta(carta);
	if (!nombreArchivo) {
		return null;
	}

	const entrada = Object.entries(CARTAS_IMAGENES).find(([ruta]) => ruta.endsWith(nombreArchivo));
	return entrada?.[1] ?? null;
}

function describirCarta(carta) {
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
					{cartasVisibles.map((carta, index) => {
						const rutaCarta = obtenerRutaCarta(carta);

						if (!rutaCarta) {
							return null;
						}

						if (!puedeSeleccionar) {
							return (
								<img
									key={`${carta}-${index}`}
									className="cartas-propias__carta"
									src={rutaCarta}
									alt={describirCarta(carta)}
									role="listitem"
								/>
							);
						}

						const cartaSeleccionada = cartasSeleccionadasVisibles.includes(carta);

						return (
							<button
								key={`${carta}-${index}`}
								type="button"
								className={`cartas-propias__carta-boton${cartaSeleccionada ? " cartas-propias__carta-boton--selected" : ""}`}
								aria-pressed={cartaSeleccionada}
								onClick={() => onToggleCarta(carta)}
								role="listitem"
							>
								<img
									className="cartas-propias__carta"
									src={rutaCarta}
									alt={describirCarta(carta)}
								/>
							</button>
						);
					})}
				</div>
			)}
		</section>
	);
}