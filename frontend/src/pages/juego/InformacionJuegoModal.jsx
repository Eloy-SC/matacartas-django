import { INFORMACION_JUEGO } from "./informacionJuegoConfig.js";

export default function InformacionJuegoModal({ onClose }) {
	const { titulo, columnas, filas } = INFORMACION_JUEGO;

	return (
		<div className="juego-informacion-modal" role="dialog" aria-modal="true" aria-labelledby="informacion-juego-title">
			<div className="juego-informacion-modal__header">
				<h2 id="informacion-juego-title">{titulo}</h2>
				<button type="button" className="juego-informacion-modal__close" onClick={onClose} aria-label="Cerrar información">
					×
				</button>
			</div>
			<table className="juego-informacion-modal__table">
				<thead>
					<tr>
						{columnas.map((columna) => <th key={columna} scope="col">{columna}</th>)}
					</tr>
				</thead>
				<tbody>
					{filas.map((fila) => (
						<tr key={fila[0]}>
							{fila.map((celda, indice) => (
								<td key={`${fila[0]}-${indice}`}>{celda}</td>
							))}
						</tr>
					))}
				</tbody>
			</table>
            <div>
                <span style={{ fontSize: '0.85rem', fontWeight: 'bold' }}>La columna de "Amenazas" contiene la(s) carta(s) que pueden matar a la(s) carta(s) de la columna "Carta".</span>
            </div>
		</div>
	);
}
