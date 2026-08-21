import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import cabecera from "../assets/cabecera.png";
import fondoContenedores from "../assets/fondo_contenedores.png";

import { obtenerCsrfToken } from "../utils/ObtenerCsfrToken";


export default function VerificarEmail() {
    const { uid, token } = useParams();
    const navigate = useNavigate();

    const [estado, setEstado] = useState("verificando");
    const [mensaje, setMensaje] = useState("");

    useEffect(() => {
        const verificarEmail = async () => {
            try {
                const csrfToken = await obtenerCsrfToken();

                const response = await fetch(
                    "/api/auth/verificar-email/",
                    {
                        method: "POST",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": csrfToken,
                        },
                        body: JSON.stringify({
                            uid: uid,
                            token: token,
                        }),
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    setEstado("error");
                    setMensaje(
                        data.detail ||
                        "No se ha podido verificar el correo electrónico."
                    );
                    return;
                }

                setEstado("correcto");
                setMensaje(
                    data.detail ||
                    "Tu correo electrónico ha sido verificado correctamente."
                );

            } catch (error) {
                console.error(
                    "Error al verificar el correo:",
                    error
                );

                setEstado("error");
                setMensaje(
                    "Se ha producido un error al verificar el correo electrónico."
                );
            }
        };

        verificarEmail();
    }, [uid, token]);

    const irAlLogin = () => {
        navigate("/login");
    };

    return (
        <div className="app">
            <img src={cabecera} alt="Matacartas" style={{maxWidth: "100%", height: "auto"}} />

            <div className="form-card" style={{ "--form-card-texture": `url(${fondoContenedores})` }}>
                {estado === "verificando" && (
                    <div style={{ marginBottom: "20px" }}>
                        <p style={{ fontWeight: "bold" }}>
                            Estamos comprobando tu enlace de
                            verificación...
                        </p>
                    </div>
                )}

                {estado === "correcto" && (
                    <div style={{ marginBottom: "20px" }}>
                        <p style={{ fontWeight: "bold", color: "green" }}>✓ Correo verificado</p>

                        <p>
                            {mensaje}
                        </p>

                        <button
                            type="button"
                            onClick={irAlLogin}
                        >
                            Ir al inicio de sesión
                        </button>
                    </div>
                )}

                {estado === "error" && (
                    <div style={{ marginBottom: "20px" }}>
                        <p style={{ fontWeight: "bold", color: "red" }}>✗ Error al verificar el correo</p>

                        <p>
                            {mensaje}
                        </p>

                        <button
                            type="button"
                            onClick={irAlLogin}
                        >
                            Volver al inicio de sesión
                        </button>
                    </div>
                )}
            </div>

        </div>
    );
}