function ordenarEntradasPorRonda(registro) {
    if (!registro || typeof registro !== "object") {
        return [];
    }

    return Object.entries(registro)
        .sort((a, b) => Number(a[0]) - Number(b[0]));
}

export default function ResumenManoPanel({
    cuentaAtras,
    ganador,
    resumenMano,
    cargandoResumen,
    errorResumen,
    esUltimaMano,
}) {
    const ticketsUsados = ordenarEntradasPorRonda(resumenMano?.tickets_usados);
    const victorias = ordenarEntradasPorRonda(resumenMano?.victorias);
    const muertes = ordenarEntradasPorRonda(resumenMano?.muertes);
    const retiradas = ordenarEntradasPorRonda(resumenMano?.retiradas);
    const efectosInmediatosRonda = ordenarEntradasPorRonda(resumenMano?.efectos_inmediatos_ronda);
    const efectosExtraFinMano = resumenMano?.efectos_extra_fin_mano || [];

    return (
        <div className="resumen-mano-panel" role="status" aria-live="polite">
            <p className="resumen-mano-panel__title">
                {esUltimaMano ? "Resumen final de partida" : "Resumen de la mano"}
            </p>
            <p className="resumen-mano-panel__countdown">
                {esUltimaMano ? "Finalizando partida" : "Siguiente mano"} en {cuentaAtras} s.
            </p>

            <p className="resumen-mano-panel__winner">
                Ganador: {ganador ?? "Sin ganador"}
            </p>

            {cargandoResumen ? (
                <p className="resumen-mano-panel__loading">Cargando resumen...</p>
            ) : errorResumen ? (
                <p className="resumen-mano-panel__error">{errorResumen}</p>
            ) : (
                <div className="resumen-mano-panel__sections">
                    <div>
                        <p className="resumen-mano-panel__subtitle">Victorias</p>
                        {victorias.length === 0 ? (
                            <p className="resumen-mano-panel__empty">Sin victorias registradas.</p>
                        ) : (
                            victorias.map(([ronda, valor]) => (
                                <p key={`victoria-${ronda}`} className="resumen-mano-panel__line">
                                    Ronda {ronda}: {Array.isArray(valor) ? `${valor[0]} (${valor[1]})` : String(valor)}
                                </p>
                            ))
                        )}
                    </div>

                    <div>
                        <p className="resumen-mano-panel__subtitle">Muertes</p>
                        {muertes.length === 0 ? (
                            <p className="resumen-mano-panel__empty">Sin muertes registradas.</p>
                        ) : (
                            muertes.map(([ronda, valor]) => (
                                <p key={`muerte-${ronda}`} className="resumen-mano-panel__line">
                                    Ronda {ronda}: {Array.isArray(valor) ? `${valor[0]} derrotó a ${valor[1]}` : String(valor)}
                                </p>
                            ))
                        )}
                    </div>

                    <div>
                        <p className="resumen-mano-panel__subtitle">Retiradas</p>
                        {retiradas.length === 0 ? (
                            <p className="resumen-mano-panel__empty">Sin retiradas registradas.</p>
                        ) : (
                            retiradas.map(([ronda, valor]) => (
                                <p key={`retirada-${ronda}`} className="resumen-mano-panel__line">
                                    Ronda {ronda}: {Array.isArray(valor) && valor.length > 0 ? valor.join(", ") : "Sin retiradas"}
                                </p>
                            ))
                        )}
                    </div>

                    <div>
                        <p className="resumen-mano-panel__subtitle">Efectos Inmediatos</p>
                        {efectosInmediatosRonda.length === 0 ? (
                            <p className="resumen-mano-panel__empty">Sin efectos inmediatos registrados.</p>
                        ) : (
                            efectosInmediatosRonda.map(([ronda, valor]) => (
                                <p key={`efecto-${ronda}`} className="resumen-mano-panel__line">
                                    Ronda {ronda}: {String(valor)}
                                </p>
                            ))
                        )}
                    </div>

                    <div>
                        <p className="resumen-mano-panel__subtitle">Efectos Extra al Final de la Mano</p>
                        {efectosExtraFinMano.length === 0 ? (
                            <p className="resumen-mano-panel__empty">Sin efectos extra registrados.</p>
                        ) : (
                            efectosExtraFinMano.map((efecto, index) => (
                                <p key={`efecto-extra-${index}`} className="resumen-mano-panel__line">
                                    {String(efecto)}
                                </p>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}