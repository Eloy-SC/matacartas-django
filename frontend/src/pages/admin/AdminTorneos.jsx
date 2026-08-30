import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { formatApiError } from "../../utils/ApiErrors.jsx";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";

export default function AdminTorneos() {
    const navigate = useNavigate();
    const [rangos, setRangos] = useState([]);
    const [rangosLoading, setRangosLoading] = useState(true);
    const [rangosError, setRangosError] = useState("");
    const [rangoMinimoId, setRangoMinimoId] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [successMessage, setSuccessMessage] = useState("");

    useEffect(() => {
        let cancelled = false;
        setRangosLoading(true);
        setRangosError("");

        fetch("/api/rangos/listar/", {
            method: "GET",
            credentials: "include",
        })
            .then(async (res) => {
                const data = await res.json().catch(() => ([]));
                if (cancelled) return;
                if (!res.ok) {
                    const detail = data?.detail || "No se pudieron cargar los rangos";
                    throw new Error(detail);
                }
                setRangos(Array.isArray(data) ? data : []);
            })
            .catch((e) => {
                if (cancelled) return;
                setRangosError(e instanceof Error ? e.message : "Error cargando rangos");
                setRangos([]);
            })
            .finally(() => {
                if (cancelled) return;
                setRangosLoading(false);
            });

        return () => {
            cancelled = true;
        };
    }, []);

    useEffect(() => {
        let cancelled = false;

        fetch("/api/config-global/rango-minimo/torneos/", {
            method: "GET",
            credentials: "include",
        })
            .then(async (res) => {
                const data = await res.json().catch(() => ({}));
                if (cancelled) return;
                if (!res.ok) {
                    throw new Error(data?.detail || "No se pudo cargar el rango mínimo");
                }
                setRangoMinimoId(data?.id ? String(data.id) : "");
            })
            .catch(() => {
                if (!cancelled) setRangoMinimoId("");
            });

        return () => {
            cancelled = true;
        };
    }, []);

    const rangoPlaceholder = rangosLoading
		? "Cargando rangos..."
		: rangosError
			? "Error cargando rangos"
			: "Ninguno";

    async function handleSubmit(event) {
        event.preventDefault();
        setError("");
        setSuccessMessage("");

        const formData = new FormData(event.currentTarget);
        const rangoMinimoValue = formData.get("rangoMinimo");

        const payload = {
            rango_id: rangoMinimoValue ? Number(rangoMinimoValue) : null,
        };

        setLoading(true);
        try {
            const csrfToken = await obtenerCsrfToken();

            const res = await fetch("/api/config-global/rango-minimo/torneos/admin/", {
                method: "PUT",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify(payload),
            });

            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                throw new Error(formatApiError(data) || "No se pudo actualizar el rango mínimo");
            }

            setSuccessMessage("Rango mínimo actualizado");
            navigate("/admin/torneos");
        } catch (e) {
            setError(e instanceof Error ? e.message : "Error creando partida");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="app">
            <button className="admin-volver-button" onClick={() => navigate("/admin")}>⮜</button>
			<div className="admin-title-card">
				<h1 style={{ marginBottom: 0 }}>ADMINISTRACION - TORNEOS</h1>
			</div>

            <div className="admin-form-card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <form onSubmit={handleSubmit}>
                    <div style={{ marginTop: 12 }}>
						<label htmlFor="rangoMinimo">Rango necesario para crear torneos</label>
						<br />
						<select
							id="rangoMinimo"
							name="rangoMinimo"
                            value={rangoMinimoId}
                            onChange={(event) => setRangoMinimoId(event.target.value)}
							disabled={rangosLoading || Boolean(rangosError)}
						>
							<option value="">{rangoPlaceholder}</option>
							{rangos.map((rango) => (
								<option key={rango.id} value={rango.id}>
									{rango.nombre}
								</option>
							))}
						</select>
					</div>
                    <div style={{ marginTop: 12 }}>
                        <button type="submit" className="admin-primary-button" disabled={loading || rangosLoading || Boolean(rangosError)}>
                            Guardar
                        </button>
                    </div>
                    {error && (
						<p role="alert" style={{ marginTop: 12, whiteSpace: "pre-line", color: "red", fontWeight: "bold" }}>
							{error}
						</p>
					)}
					{successMessage && (
						<p style={{ marginTop: 12, color: "green", fontWeight: "bold" }}>{successMessage}</p>
					)}
                </form>
            </div>
        </div>
    );
}