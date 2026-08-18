import { Fragment } from "react";
import DiccionarioTicketsFront from "./DiccionarioTicketsFront";

const RONDAS = [
    ["ronda_prep", "Preparativos"],
    ["ronda_1", "Ronda 1"],
    ["ronda_2", "Ronda 2"],
    ["ronda_3", "Ronda 3"],
    ["ronda_com", "Ronda de comodines"],
];

const COLORJUGADOR = {
    rojo: "red",
    naranja: "orange",
    amarillo: "goldenrod",
    verde: "green",
    azul: "blue",
    morado: "purple",
}

const equivalenciasEfectosInmediatos = {
    "VINOS_VIEJOS": " ha recibido 2 puntos por el efecto de su carta de vinos viejos.",
    "SAQUEADOR": " ha recibido puntos por el efecto del Saqueador de Tumbas que ha utilizado.",
};

const equivalenciasVictorias = {
    "RETIRADAS": "la retirada del(los) rival(es).",
    "MARTIRIZADO": "el efecto especial del Martirizado.",
    "MAYOR_FUERZA": "carta de mayor fuerza.",
    "CORRUPTOR": "haber corrompido la muerte de la ronda, gracias al Corruptor.",
    "MUERTE": "haber matado a la carta más alta.",
    "CONTRAATAQUE": "haber contraatacado a la carta asesina.",
    "DESEMPATE_COMODINES": "poseer el comodín de mayor riqueza."
};

const equivalenciasEfectosFinMano = {
    "JOYAS_REALES_3": " ha recibido 3 puntos por haber utilizado más de una carta de joyas reales durante la mano.",
    "JOYAS_REALES_2": " ha recibido 2 puntos por haber utilizado una carta de joyas reales durante la mano.",
    "CARTA_UNICA": " ha recibido 4 puntos por haber ganado la mano utilizando una carta única.",
    "MERCADER": " ha recibido puntos por el efecto del Mercader.",
    "REBELDE": " ha recibido puntos por el efecto del Rebelde.",
    "SEGADOR": " ha recibido puntos por el efecto del Segador.",
    "MONEDERO": " ha recibido puntos por el efecto del Monedero Peculiar.",
};

function nombreDeTicket(ticket) {
    if (typeof ticket !== "string" || ticket.length === 0) {
        return "Ticket desconocido";
    }

    const info = DiccionarioTicketsFront[ticket];
    return info?.nombre ?? ticket;
}

export default function ResumenManoPanel({
    cuentaAtras,
    ganador,
    resumenMano,
    cargandoResumen,
    errorResumen,
    esUltimaMano,
}) {
    const ganadorResumen = resumenMano?.ganador ?? ganador;
    const numeroMano = resumenMano?.mano_num;
    const efectosExtraFinMano = resumenMano?.efectos_extra_fin_mano ?? [];

    return (
        <div className="resumen-mano-panel" role="status" aria-live="polite">
            <p className="resumen-mano-panel__title">
                {esUltimaMano ? "Resumen final de partida" : "Resumen de la mano"}
            </p>
            <p className="resumen-mano-panel__countdown">
                {esUltimaMano ? "Finalizando partida" : "Siguiente mano"} en {cuentaAtras} s.
            </p>

            {typeof numeroMano === "number" ? (
                <p className="resumen-mano-panel__winner">Mano {numeroMano}</p>
            ) : null}

            {cargandoResumen ? (
                <p className="resumen-mano-panel__loading">Cargando resumen...</p>
            ) : errorResumen ? (
                <p className="resumen-mano-panel__error">{errorResumen}</p>
            ) : (
                <div className="resumen-mano-panel__sections">
                    {RONDAS.map(([claveRonda, etiquetaRonda]) => {
                        const ronda = resumenMano?.[claveRonda] ?? null;
                        const victoria = ronda?.victoria;
                        const muerte = ronda?.muerte;
                        const retiradas = ronda?.retiradas ?? [];
                        const lista = ronda?.efectos_inmediatos ?? [];
                        const efectosInmediatos = lista.map(([color, metodo]) => [
                            color,
                            equivalenciasEfectosInmediatos[metodo] ?? metodo
                        ]);
                        const ticketsUsados = ronda?.tickets_usados ?? [];

                        return (
                            <div key={claveRonda}>
                                <p className="resumen-mano-panel__subtitle">{etiquetaRonda}</p>
                                {victoria ? (
                                    <p className="resumen-mano-panel__line"><span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[victoria[0]] }}>{victoria[0]}</span> ha ganado la ronda por {equivalenciasVictorias[victoria[1]]}.</p>
                                ) : null}
                                {muerte ? (
                                    <p className="resumen-mano-panel__line"><span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[muerte[0]] }}>{muerte[0]}</span> ha matado a <span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[muerte[1]] }}>{muerte[1]}</span>.</p>
                                ) : null}
                                {retiradas.length > 1 ? (
                                    <p className="resumen-mano-panel__line">
                                        Los jugadores{" "}
                                        {retiradas.map((color, index) => (
                                            <Fragment key={color}>
                                                <span
                                                    className="juego-resumen-overlay__label"
                                                    style={{ color: COLORJUGADOR[color] }}
                                                >
                                                    {color}
                                                </span>
                                                {index < retiradas.length - 1 ? ", " : ""}
                                            </Fragment>
                                        ))}
                                        {" "}se han retirado.
                                    </p>
                                ) : retiradas.length === 1 ? (
                                    <p className="resumen-mano-panel__line">El jugador <span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[retiradas[0]] }}>{retiradas[0]}</span> se ha retirado.</p>
                                ) : null}
                                {efectosInmediatos.length > 0
                                    ? efectosInmediatos.map(([jugador, efecto], index) => (
                                        <p
                                            key={index}
                                            className="resumen-mano-panel__line"
                                        >
                                            El jugador <span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[jugador] }}>{jugador}</span>{efecto}
                                        </p>
                                    ))
                                    : null}
                                {ticketsUsados.length > 0 ? ticketsUsados.map(([jugador, ticket], index) => (
                                        <p
                                            key={index}
                                            className="resumen-mano-panel__line"
                                        >
                                            El jugador <span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[jugador] }}>{jugador}</span> ha usado el ticket <span className="juego-resumen-overlay__label">{nombreDeTicket(ticket)}</span>.
                                        </p>
                                    )) : null}

                                {!victoria && !muerte && retiradas.length === 0 && efectosInmediatos.length === 0 && ticketsUsados.length === 0 ? (
                                    <p className="resumen-mano-panel__empty">Sin eventos registrados.</p>
                                ) : null}
                            </div>
                        );
                    })}

                    <div>
                        <p className="resumen-mano-panel__subtitle">Final de la mano</p>
                        {efectosExtraFinMano.length > 0
                                    ? efectosExtraFinMano.map(([jugador, efecto], index) => (
                                        <p
                                            key={index}
                                            className="resumen-mano-panel__line"
                                        >
                                            El jugador <span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[jugador] }}>{jugador}</span>{equivalenciasEfectosFinMano[efecto]}
                                        </p>
                                    ))
                                    : null}
                        <p className="resumen-mano-panel__line">
                            El jugador <span className="juego-resumen-overlay__label" style={{ color: COLORJUGADOR[ganadorResumen] }}> {ganadorResumen}</span> ha ganado la mano.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}