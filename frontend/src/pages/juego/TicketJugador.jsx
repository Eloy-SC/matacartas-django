import { createPortal } from "react-dom";
import { useRef, useState } from "react";
import DiccionarioTicketsFront from "./DiccionarioTicketsFront";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";
import "../../styles/cartas_propias.css";

import ticket0 from "../../assets/tickets/ticket_0.png";
import ticket1 from "../../assets/tickets/ticket_1.png";
import ticket2 from "../../assets/tickets/ticket_2.png";
import ticket3 from "../../assets/tickets/ticket_3.png";

function normalizarClaseTicket(clase) {
  if (typeof clase === "number" && Number.isFinite(clase)) {
    return clase;
  }

  if (typeof clase !== "string") {
    return 1;
  }

  const claseNormalizada = clase.trim().toLowerCase();

  if (claseNormalizada === "Clase Imperial") {
    return 0;
  }

  if (claseNormalizada === "1ª clase") {
    return 1;
  }

  if (claseNormalizada === "2ª clase") {
    return 2;
  }

  if (claseNormalizada === "3ª clase") {
    return 3;
  }

  const claseComoNumero = Number.parseInt(claseNormalizada, 10);
  return Number.isFinite(claseComoNumero) ? claseComoNumero : 1;
}

export default function TicketJugador({ ticket, ticket_usable, ronda_actual, cambios, es_turno_actual, es_fin_mano, partidaId, loadMesa }) {
  const [hover, setHover] = useState(false);
  const botonRef = useRef(null);

  if (!ticket) {
    return (
      <div className="ticket-jugador ticket-jugador--vacio" aria-hidden>
        <p>No tienes ticket</p>
      </div>
    );
  }

  const info = DiccionarioTicketsFront[ticket] ?? { nombre: ticket, clase: "?", descripcion: "" };
  const claseTicket = normalizarClaseTicket(info.clase);

  const imagenPorClase = {
    0: ticket0,
    1: ticket1,
    2: ticket2,
    3: ticket3,
  };

  const imagenTicket = imagenPorClase[claseTicket] ?? imagenPorClase[1];

  const puedeUsarTicket = (() => {
      if (es_fin_mano) {
          return false;
      } else {
        switch (ticket_usable) {
            case "general":
                return es_turno_actual;

            case "ronda":
                return es_turno_actual && ronda_actual > 0;

            case "cambios":
                return es_turno_actual && ronda_actual === 0 && cambios === 0;

            default:
                return false;
        }
      }
  })();

  const usarTicket = async () => {
    try {
      const csrfToken = await obtenerCsrfToken();
      const res = await fetch(`/api/partida/${partidaId}/mano/ronda/usar-ticket/`, {
        method: "PUT",
        credentials: "include",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify({ ticket }),
      });

      let data;
      try {
        data = await res.json();
      } catch (err) {
        const text = await res.text().catch(() => "");
        // eslint-disable-next-line no-console
        console.error("usar-ticket response text:", text);
        data = { detail: text };
      }

      if (!res.ok) {
        // eslint-disable-next-line no-console
        console.error("usar-ticket status:", res.status, data);
        throw new Error(data?.detail || `Error usando el ticket (status ${res.status})`);
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
      <button
        ref={botonRef}
        type="button"
        className="ticket-jugador__boton"
        onClick={usarTicket}
        aria-label={`Usar ticket ${info.nombre}`}
        disabled={!puedeUsarTicket}
      >
        <img src={imagenTicket} alt={info.nombre} className="ticket-jugador__imagen" />
      </button>

      {hover && botonRef.current && typeof document !== "undefined"
        ? createPortal(
            <div
              className="cartas-propias__tooltip"
              role="tooltip"
              style={{
                position: "fixed",
                left: `${botonRef.current.getBoundingClientRect().right + 12}px`,
                top: `${botonRef.current.getBoundingClientRect().top + botonRef.current.getBoundingClientRect().height / 2}px`,
                right: "auto",
                bottom: "auto",
                transform: "translateY(-50%)",
                display: "block",
                width: "max-content",
                maxWidth: "min(320px, calc(100vw - 24px))",
                boxSizing: "border-box",
                zIndex: 99999,
                pointerEvents: "none",
              }}
            >
              <p className="cartas-propias__tooltip-titulo">{info.nombre}</p>
              <p className="cartas-propias__tooltip-tipo">{info.clase}</p>
              {info.descripcion ? <p className="cartas-propias__tooltip-efecto">{info.descripcion}</p> : null}
            </div>,
            document.body,
          )
        : null}
    </div>
  );
}
