const CARTAS_IMAGENES = import.meta.glob("../../assets/cartas/*.png", {
	eager: true,
	import: "default",
});

export const CARTAS_A_IMAGEN = {
	"2_OROS": "carta_oros_2.png",
	"3_OROS": "carta_oros_3.png",
	"4_OROS": "carta_oros_4.png",
	"5_OROS": "carta_oros_5.png",
	"6_OROS": "carta_oros_6.png",
	"7_OROS": "carta_oros_7.png",
	"8_OROS": "carta_oros_8.png",
	"9_OROS": "carta_oros_9.png",
	"10_OROS": "carta_oros_10.png",
	"11_OROS": "carta_oros_11.png",
	"12_OROS": "carta_oros_12.png",
	"1_OROS": "carta_oros_1.png",
	"2_COPAS": "carta_copas_2.png",
	"3_COPAS": "carta_copas_3.png",
	"4_COPAS": "carta_copas_4.png",
	"5_COPAS": "carta_copas_5.png",
	"6_COPAS": "carta_copas_6.png",
	"7_COPAS": "carta_copas_7.png",
	"8_COPAS": "carta_copas_8.png",
	"9_COPAS": "carta_copas_9.png",
	"10_COPAS": "carta_copas_10.png",
	"11_COPAS": "carta_copas_11.png",
	"12_COPAS": "carta_copas_12.png",
	"1_COPAS": "carta_copas_1.png",
	"2_BASTOS": "carta_bastos_2.png",
	"3_BASTOS": "carta_bastos_3.png",
	"4_BASTOS": "carta_bastos_4.png",
	"5_BASTOS": "carta_bastos_5.png",
	"6_BASTOS": "carta_bastos_6.png",
	"7_BASTOS": "carta_bastos_7.png",
	"8_BASTOS": "carta_bastos_8.png",
	"9_BASTOS": "carta_bastos_9.png",
	"10_BASTOS": "carta_bastos_10.png",
	"11_BASTOS": "carta_bastos_11.png",
	"12_BASTOS": "carta_bastos_12.png",
	"1_BASTOS": "carta_bastos_1.png",
	"2_ESPADAS": "carta_espadas_2.png",
	"3_ESPADAS": "carta_espadas_3.png",
	"4_ESPADAS": "carta_espadas_4.png",
	"5_ESPADAS": "carta_espadas_5.png",
	"6_ESPADAS": "carta_espadas_6.png",
	"7_ESPADAS": "carta_espadas_7.png",
	"8_ESPADAS": "carta_espadas_8.png",
	"9_ESPADAS": "carta_espadas_9.png",
	"10_ESPADAS": "carta_espadas_10.png",
	"11_ESPADAS": "carta_espadas_11.png",
	"12_ESPADAS": "carta_espadas_12.png",
	"1_ESPADAS": "carta_espadas_1.png",
	"3_JOYAS_REALES": "carta_joyas_3.png",
	"4_JOYAS_REALES": "carta_joyas_4.png",
	"5_JOYAS_REALES": "carta_joyas_5.png",
	"6_JOYAS_REALES": "carta_joyas_6.png",
	"7_JOYAS_REALES": "carta_joyas_7.png",
	"8_JOYAS_REALES": "carta_joyas_8.png",
	"9_JOYAS_REALES": "carta_joyas_9.png",
	"3_VINOS_VIEJOS": "carta_vinos_3.png",
	"4_VINOS_VIEJOS": "carta_vinos_4.png",
	"5_VINOS_VIEJOS": "carta_vinos_5.png",
	"6_VINOS_VIEJOS": "carta_vinos_6.png",
	"7_VINOS_VIEJOS": "carta_vinos_7.png",
	"8_VINOS_VIEJOS": "carta_vinos_8.png",
	"9_VINOS_VIEJOS": "carta_vinos_9.png",
	"2_BASTOS_PUNTIAGUDOS": "carta_bastospun_2.png",
	"3_BASTOS_PUNTIAGUDOS": "carta_bastospun_3.png",
	"4_BASTOS_PUNTIAGUDOS": "carta_bastospun_4.png",
	"5_BASTOS_PUNTIAGUDOS": "carta_bastospun_5.png",
	"6_BASTOS_PUNTIAGUDOS": "carta_bastospun_6.png",
	"7_BASTOS_PUNTIAGUDOS": "carta_bastospun_7.png",
	"8_BASTOS_PUNTIAGUDOS": "carta_bastospun_8.png",
	"9_BASTOS_PUNTIAGUDOS": "carta_bastospun_9.png",
	"10_BASTOS_PUNTIAGUDOS": "carta_bastospun_10.png",
	"11_BASTOS_PUNTIAGUDOS": "carta_bastospun_11.png",
	"12_BASTOS_PUNTIAGUDOS": "carta_bastospun_12.png",
	"1_BASTOS_PUNTIAGUDOS": "carta_bastospun_1.png",
	"2_ESPADAS_ESCUDOS": "carta_espesc_2.png",
	"3_ESPADAS_ESCUDOS": "carta_espesc_3.png",
	"4_ESPADAS_ESCUDOS": "carta_espesc_4.png",
	"5_ESPADAS_ESCUDOS": "carta_espesc_5.png",
	"6_ESPADAS_ESCUDOS": "carta_espesc_6.png",
	"7_ESPADAS_ESCUDOS": "carta_espesc_7.png",
	"8_ESPADAS_ESCUDOS": "carta_espesc_8.png",
	"9_ESPADAS_ESCUDOS": "carta_espesc_9.png",
	"10_ESPADAS_ESCUDOS": "carta_espesc_10.png",
	"11_ESPADAS_ESCUDOS": "carta_espesc_11.png",
	"12_ESPADAS_ESCUDOS": "carta_espesc_12.png",
	"1_ESPADAS_ESCUDOS": "carta_espesc_1.png",
	"SAQUEADOR_TUMBAS": "carta_saqueador.png",
	"CORRUPTOR": "carta_corruptor.png",
	"MERCADER": "carta_mercader.png",
	"MONEDERO_PECULIAR": "carta_monedero.png",
	"AS_EXTRANJERO": "carta_as_extranjero.png",
	"BUFON": "carta_bufon.png",
	"SEGADOR": "carta_segador.png",
	"REBELDE": "carta_rebelde.png",
	"DON_DINERO": "carta_rey_don_dinero.png",
	"MARTIRIZADO": "carta_martirizado.png",
};

export function obtenerRutaCarta(carta) {
	if (typeof carta !== "string") {
		return null;
	}

	const nombreArchivo = CARTAS_A_IMAGEN[carta.trim().toUpperCase()];
	if (!nombreArchivo) {
		return null;
	}

	const entrada = Object.entries(CARTAS_IMAGENES).find(([ruta]) => ruta.endsWith(nombreArchivo));
	return entrada?.[1] ?? null;
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
}) {
	const rutaCarta = obtenerRutaCarta(carta);

	if (!rutaCarta) {
		return null;
	}

	const key = `${carta}-${index}`;
	const cartaDescripcion = describirCarta(carta);

	if (!seleccionable || typeof onToggleCarta !== "function") {
		return (
			<img
				key={key}
				className="cartas-propias__carta"
				src={rutaCarta}
				alt={cartaDescripcion}
				role="listitem"
			/>
		);
	}

	return (
		<button
			key={key}
			type="button"
			className={`cartas-propias__carta-boton${seleccionada ? " cartas-propias__carta-boton--selected" : ""}`}
			aria-pressed={seleccionada}
			onClick={() => onToggleCarta(carta)}
			role="listitem"
		>
			<img
				className="cartas-propias__carta"
				src={rutaCarta}
				alt={cartaDescripcion}
			/>
		</button>
	);
}