import { useEffect, useState } from "react";
import "../styles/rangos.css";

export default function UserRango({ userId, className = "" }) {
  const [rango, setRango] = useState({ nombre: "", color: "" });

  useEffect(() => {
    let cancelled = false;

    async function loadRango() {
      if (!userId) {
        setRango({ nombre: "", color: "" });
        return;
      }

      try {
        const res = await fetch(`/api/rangos/usuario/${userId}/`, {
          method: "GET",
          credentials: "include",
        });
        const data = await res.json().catch(() => ({}));

        if (cancelled) return;

        if (!res.ok) {
          setRango({ nombre: "", color: "" });
          return;
        }

        setRango({
          nombre: data?.nombre ?? "",
          color: data?.color ?? "",
        });
      } catch (e) {
        if (cancelled) return;
        setRango({ nombre: "", color: "" });
      }
    }

    loadRango();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  const rangoClass = (rango.color ?? "")
    .replace(/_/g, "-")
    .toLowerCase();

  return (
    <span className={`rango-text ${rangoClass ? `rango-color-${rangoClass}` : ""} ${className}`.trim()}>
      {rango.nombre}
    </span>
  );
}