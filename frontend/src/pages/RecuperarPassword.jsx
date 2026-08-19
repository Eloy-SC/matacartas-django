import { useState } from "react";
import cabecera from "../assets/cabecera.png";
import fondoContenedores from "../assets/fondo_contenedores.png";

export default function RecuperarPassword() {
    const [email, setEmail] = useState("");
    const [mensaje, setMensaje] = useState("");
    const [error, setError] = useState("");
    const [cargando, setCargando] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        setMensaje("");
        setError("");
        setCargando(true);

        try {
            const response = await fetch(
                "/api/auth/password-reset/",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: "include",
                    body: JSON.stringify({
                        email: email,
                    }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    "No se ha podido procesar la solicitud."
                );
            }

            setMensaje(data.detail);
            setEmail("");

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
                    Introduce el correo asociado a tu cuenta para <br></br>
                    poder enviar las instrucciones de reestablecimiento <br></br>
                    de contraseña.
                </p>

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: 20 }}>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Correo electrónico"
                            required
                        />
                    </div>
                    
                    <div>
                        <button
                            type="submit"
                            disabled={cargando}
                        >
                            {cargando
                                ? "Enviando..."
                                : "Enviar instrucciones"}
                        </button>
                        <button
                            type="button"
                            disabled={cargando}
                            style={{ marginLeft: 8 }}
                            onClick={() => navigate("/login")}
                        >
                            Volver
                        </button>
                    </div>
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