import cartaBocaAbajo from "../../assets/cartas/carta_boca_abajo.png";
import defaultProfilePic from "../../assets/default_profile_pic.png";
import { describirCarta, obtenerRutaCarta } from "./RenderizadoCartas.jsx";
import "../../styles/mesa.css";

const POSICIONES_POR_CONTRINCANTES = {
	1: ["ARRIBA_CENTRO"],
	2: ["ARRIBA_DCHA", "ARRIBA_IZQ"],
	3: ["DERECHA", "ARRIBA_CENTRO", "IZQUIERDA"],
	4: ["DERECHA", "ARRIBA_DCHA", "ARRIBA_IZQ", "IZQUIERDA"],
	5: ["DERECHA", "ARRIBA_DCHA", "ARRIBA_CENTRO", "ARRIBA_IZQ", "IZQUIERDA"],
};

const COORDENADAS_POR_POSICION = {
	DERECHA: { top: "65%", right: "3%" },
	ARRIBA_DCHA: { top: "11%", right: "30%" },
	ARRIBA_CENTRO: { top: "5%", left: "50%" },
	ARRIBA_IZQ: { top: "11%", left: "30%" },
	IZQUIERDA: { top: "65%", left: "3%" },
};

const COLORJUGADOR = {
    rojo: "red",
    naranja: "orange",
    amarillo: "yellow",
    verde: "green",
    azul: "blue",
    morado: "purple",
}

const ALTO_CARTA = 96;
const DESPLAZAMIENTO_CARTAS = 16;

function obtenerColoresContrincantesEnOrden(coloresMesa, colorJugador) {
	if (!Array.isArray(coloresMesa) || coloresMesa.length === 0) {
		return [];
	}

	const indiceJugador = coloresMesa.indexOf(colorJugador);
	if (indiceJugador === -1) {
		return coloresMesa.filter((color) => color !== colorJugador);
	}

	const coloresOrdenados = [];
	for (let offset = 1; offset < coloresMesa.length; offset += 1) {
		coloresOrdenados.push(coloresMesa[(indiceJugador + offset) % coloresMesa.length]);
	}

	return coloresOrdenados;
}

function ordenarContrincantes(contrincantes, coloresOrdenados) {
	const contrincantesPorColor = new Map();
	contrincantes.forEach((contrincante) => {
		if (contrincante?.color) {
			contrincantesPorColor.set(contrincante.color, contrincante);
		}
	});

	const contrincantesOrdenados = coloresOrdenados
		.map((color) => contrincantesPorColor.get(color))
		.filter(Boolean);

	if (contrincantesOrdenados.length === contrincantes.length) {
		return contrincantesOrdenados;
	}

	const contrincantesRestantes = contrincantes.filter(
		(contrincante) => !contrincantesOrdenados.includes(contrincante)
	);

	return [...contrincantesOrdenados, ...contrincantesRestantes];
}

function obtenerPosicionesDisponibles(cantidadContrincantes) {
	return POSICIONES_POR_CONTRINCANTES[cantidadContrincantes] ?? POSICIONES_POR_CONTRINCANTES[5];
}

function obtenerCartasJugadasDeParticipante(rondas, colorParticipante) {
	if (!Array.isArray(rondas) || !colorParticipante) {
		return [];
	}

	return [...rondas]
		.filter((ronda) => (ronda?.ronda_num ?? 0) > 0)
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

function tieneComodinSeleccionado(participante) {
	if (typeof participante?.carta_comodin === "string") {
		return participante.carta_comodin.trim().length > 0;
	}

	return Boolean(participante?.carta_comodin);
}

function renderizarPilaCartas(cartasJugadas) {
	if (cartasJugadas.length === 0) {
		return <div className="mesa-inicial__cartas-jugadas mesa-inicial__cartas-jugadas--vacía" />;
	}

	const alturaPila = ALTO_CARTA + (cartasJugadas.length - 1) * DESPLAZAMIENTO_CARTAS;

	return (
		<div className="mesa-inicial__cartas-jugadas" style={{ height: `${alturaPila}px` }}>
			{cartasJugadas.map((carta, index) => {
				const rutaCarta = obtenerRutaCarta(carta);

				if (!rutaCarta) {
					return null;
				}

				return (
					<img
						key={`${carta}-${index}`}
						className="mesa-inicial__carta-jugada"
						style={{
							top: `${index * DESPLAZAMIENTO_CARTAS}px`,
							zIndex: index + 1,
						}}
						src={rutaCarta}
						alt={describirCarta(carta)}
					/>
				);
			})}
		</div>
	);
}

function renderizarSubcontenedorCartas(participante) {
	const cartasJugadas = obtenerCartasJugadasDeParticipante(participante?.rondas, participante?.color);
	const conComodin = tieneComodinSeleccionado(participante);

	return (
		<div className="mesa-inicial__subcontenedor-cartas">
			{conComodin ? (
				<img
					className="mesa-inicial__carta-boca-abajo"
					src={cartaBocaAbajo}
					alt="Carta boca abajo"
				/>
			) : null}
			{renderizarPilaCartas(cartasJugadas)}
		</div>
	);
}

export default function MesaInicialContrincantes({ partida, jugador, contrincantes = [], rondas = [] }) {
	const coloresMesa = Array.isArray(partida?.disposicion_jugadores) ? partida.disposicion_jugadores : [];
	const coloresContrincantes = obtenerColoresContrincantesEnOrden(coloresMesa, jugador?.color);
	const contrincantesOrdenados = ordenarContrincantes(contrincantes, coloresContrincantes);
	const posicionesDisponibles = obtenerPosicionesDisponibles(contrincantesOrdenados.length);
	const esPartidaDeSeisJugadores = coloresMesa.length === 6;

	return (
		<section className="mesa-inicial" aria-label="Posiciones iniciales de los contrincantes">
			<div className="mesa-inicial__tablero">
				{contrincantesOrdenados.map((contrincante, index) => {
					const posicion = posicionesDisponibles[index] ?? posicionesDisponibles[posicionesDisponibles.length - 1];
					const coordenadas = COORDENADAS_POR_POSICION[posicion] ?? COORDENADAS_POR_POSICION.ARRIBA_CENTRO;
					const estiloPosicion = {
						...coordenadas,
						...(esPartidaDeSeisJugadores && posicion === "ARRIBA_DCHA" ? { right: "15%" } : {}),
						...(esPartidaDeSeisJugadores && posicion === "ARRIBA_IZQ" ? { left: "15%" } : {}),
					};
					const imagen = contrincante?.imagen || defaultProfilePic;
					const colorBorde = COLORJUGADOR[contrincante?.color] || contrincante?.color || "#000000";
					const participante = {
						...contrincante,
						rondas,
					};

					return (
						<article
							key={contrincante?.contrincante_id ?? `${posicion}-${index}`}
							className={`mesa-inicial__contrincante mesa-inicial__contrincante--${posicion.toLowerCase()}`}
							style={{ ...estiloPosicion, "--seat-color": contrincante?.color || "#000000" }}
							aria-label={`Contrincante ${contrincante?.nombre ?? index + 1}`}
						>
							<div className="mesa-inicial__contrincante-card" tabIndex={0}>
								<div>
									<img
										className="mesa-inicial__avatar"
										style={{ border: `5px solid ${colorBorde}` }}
										src={imagen}
										alt={`Foto de perfil de ${contrincante.nombre ?? "contrincante"}`}
										onError={(event) => {
											event.currentTarget.src = defaultProfilePic;
										}}
									/>
								</div>
								<div>
									<span className="mesa-inicial__puntos-contrincante">
										{contrincante?.puntos ?? "?"} ptos.
									</span>
								</div>
								{renderizarSubcontenedorCartas(participante)}
								<span className="mesa-inicial__nombre-contrincante">
									{contrincante?.nombre ?? "Contrincante"}
								</span>
							</div>
						</article>
					);
				})}
			</div>
		</section>
	);
}