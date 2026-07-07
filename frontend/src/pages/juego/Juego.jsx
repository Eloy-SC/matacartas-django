
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function Juego() {
  const { partidaId } = useParams();
  const [, setJugadores] = useState([]);

  useEffect(() => {
    let cancelled = false;

    const loadJugadores = async () => {
      if (!partidaId) return;

      try {
        const res = await fetch(`/api/partidas/${partidaId}/jugadores/`, {
          method: "GET",
          credentials: "include",
        });

        const data = await res.json().catch(() => ([]));

        if (!res.ok) {
          throw new Error(data?.detail || "No se pudo cargar la lista de jugadores");
        }

        if (!cancelled) {
          setJugadores(Array.isArray(data) ? data : []);
        }
      } catch {
        if (!cancelled) {
          setJugadores([]);
        }
      }
    };

    void loadJugadores();

    return () => {
      cancelled = true;
    };
  }, [partidaId]);

  const handleRepartirCartas = async (partidaId) => {
		try {
			const csrfRes = await fetch("/api/auth/csrf/", {
				method: "GET",
				credentials: "include",
			});

			if (!csrfRes.ok) {
				throw new Error("No se pudo obtener el token CSRF");
			}

			const { csrfToken } = await csrfRes.json().catch(() => ({}));

			if (!csrfToken) {
				throw new Error("Token CSRF no disponible");
			}

      const iniciarRes = await fetch(
				`/api/partida/${partidaId}/mano/repartir/`,
				{
					method: "PUT",
					credentials: "include",
					headers: {
						"Content-Type": "application/json",
						"X-CSRFToken": csrfToken,
					},
				}
			);
    } catch (e) {
			alert(
				e instanceof Error
					? e.message
					: "Error repartiendo cartas"
			);
		}
  };

  return (
    <div className="juego-container">
      <h1>Juego</h1>
      <p>Bienvenido al juego. Aquí se desarrollará la partida.</p>

      <button
          type="button"
          className="main-primary-button"
          onClick={() => handleRepartirCartas(partidaId)}
          aria-label="Volver"
        >
				Repartir cartas
			</button>
    </div>
  );
}