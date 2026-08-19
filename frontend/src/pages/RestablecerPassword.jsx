import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import cabecera from "../assets/cabecera.png";
import fondoContenedores from "../assets/fondo_contenedores.png";
import { obtenerCsrfToken } from "../utils/ObtenerCsfrToken";

export default function RestablecerPassword() {
    const { uid, token } = useParams();
    const navigate = useNavigate();

    const [password, setPassword] = useState("");
    const [password2, setPassword2] = useState("");

    const [error, setError] = useState("");
    const [mensaje, setMensaje] = useState("");
    const [cargando, setCargando] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        setError("");
        setMensaje("");

        if (password !== password2) {
            setError("Las contraseñas no coinciden.");
            return;
        }

        setCargando(true);

        try {
            const csrfToken = await obtenerCsrfToken();

            const response = await fetch(
                "/api/auth/password-reset-confirm/",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    credentials: "include",
                    body: JSON.stringify({
                        uid: uid,
                        token: token,
                        new_password: password,
                    }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    "No se ha podido cambiar la contraseña."
                );
            }

            setMensaje(data.detail);

            setTimeout(() => {
                navigate("/login");
            }, 2000);

        } catch (error) {
            setError(error.message);
        } finally {
            setCargando(false);
        }
    };

    return (
        <div className="app">
            <img src={cabecera} alt="Matacartas" style={{maxWidth: "100%", height: "auto"}} />
            
            <div className="form-card" style={{ "--form-card-texture": `url(${fondoContenedores})` }}>

                <p style={{ fontWeight: "bold" }}>
                    Introduce la nueva contraseña para tu cuenta.
                </p>

                <form onSubmit={handleSubmit}>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) =>
                            setPassword(e.target.value)
                        }
                        placeholder="Nueva contraseña"
                        required
                    />

                    <input
                        type="password"
                        value={password2}
                        onChange={(e) =>
                            setPassword2(e.target.value)
                        }
                        placeholder="Repite la contraseña"
                        required
                    />

                    <button
                        type="submit"
                        disabled={cargando}
                    >
                        {cargando
                            ? "Cambiando..."
                            : "Cambiar contraseña"}
                    </button>
                </form>

                {mensaje && (
                    <p className="mensaje-exito">
                        {mensaje}
                    </p>
                )}

                {error && (
                    <p className="mensaje-error">
                        {error}
                    </p>
                )}
            </div>
        </div>
    );
}