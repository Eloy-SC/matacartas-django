export default function InfoSuperior({ partida, mano, jugador }) {
	const manoActual = mano?.mano_num ?? "-";
	const totalManos = partida?.longitud ?? "-";
	const puntos = jugador?.puntos ?? 0;
	const acumuladorKills = jugador?.acumulador_kills ?? 0;
	const acumuladorDeaths = jugador?.acumulador_deaths ?? 0;

	return (
		<div className="recuadro-info-superior" aria-label="Resumen de estado del jugador">
			<p className="texto-info-superior">Mano {manoActual} de {totalManos}</p>
			<p className="texto-info-superior">Tienes {puntos} puntos</p>
			<p className="texto-info-superior">Has matado {acumuladorKills} cartas</p>
			<p className="texto-info-superior">Te han matado {acumuladorDeaths} cartas</p>
		</div>
	);
}
