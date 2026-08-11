import { useState } from "react";
import DiccionarioTicketsFront from "./DiccionarioTicketsFront";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";

import ticket0 from "../../assets/tickets/ticket_0.png";
import ticket1 from "../../assets/tickets/ticket_1.png";
import ticket2 from "../../assets/tickets/ticket_2.png";
import ticket3 from "../../assets/tickets/ticket_3.png";

export default function TicketJugador({ ticket, partidaId, loadMesa }) {
  const [hover, setHover] = useState(false);

  if (!ticket) {
    return (
      <div className="ticket-jugador ticket-jugador--vacio" aria-hidden>
        <p>No tienes ticket</p>
      </div>
    );
  }

  const info = DiccionarioTicketsFront[ticket] ?? { nombre: ticket, clase: "?", descripcion: "" };

  const imagenPorClase = {
    0: ticket0,
    1: ticket1,
    2: ticket2,
    3: ticket3,
  };

  const imagenTicket = imagenPorClase[info.clase] ?? imagenPorClase[1];

  const usarTicket = async () => {
    try {
      const csrfToken = await obtenerCsrfToken();
      const res = await fetch(`/api/partida/${partidaId}/mano/ronda/usar-ticket/`, {
        method: "PUT",
        credentials: "include",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify({ ticket }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data?.detail || "Error usando el ticket");
      }

      void loadMesa({ showLoading: false });
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error("Error usando ticket:", e);
      alert(e instanceof Error ? e.message : "Error usando ticket");
    }
  };

  return (
    <div
      className="ticket-jugador"
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      <button type="button" className="ticket-jugador__boton" onClick={usarTicket} aria-label={`Usar ticket ${info.nombre}`}>
        <img src={imagenTicket} alt={info.nombre} className="ticket-jugador__imagen" />
      </button>

      {hover ? (
        <div className="ticket-jugador__tooltip" role="note">
          <div className="ticket-jugador__tooltip-nombre">{info.nombre}</div>
          <div className="ticket-jugador__tooltip-clase">{info.clase}</div>
          <div className="ticket-jugador__tooltip-desc">{info.descripcion}</div>
        </div>
      ) : null}
    </div>
  );
}
