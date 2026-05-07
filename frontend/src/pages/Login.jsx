import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/main.css";
import defaultProfilePic from "../assets/default_profile_pic.png";

export default function Login() {
  const location = useLocation();
  const navigate = useNavigate();
  const [mode, setMode] = useState("login"); // 'login' | 'register'
  const [username, setUsername] = useState("");
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [imgPreviewError, setImgPreviewError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const profilePreviewSrc = imgUrl && !imgPreviewError ? imgUrl : defaultProfilePic;
  const showProfilePreviewWarning = Boolean(imgUrl) && imgPreviewError;
  const profilePreviewWarningText =
    "No se ha podido encontrar la imagen, se asignará esta por defecto";

  function formatApiError(data) {
    if (!data) return "";
    if (typeof data === "string") return data;

    if (typeof data.detail === "string") return data.detail;

    if (typeof data === "object") {
      const parts = [];
      for (const [field, value] of Object.entries(data)) {
        if (Array.isArray(value)) {
          parts.push(`${value.join(" ")}`);
        } else if (typeof value === "string") {
          parts.push(`${value}`);
        }
      }
      return parts.join("\n");
    }

    return "";
  }

  const initialModeFromQuery = useMemo(() => {
    const params = new URLSearchParams(location.search);
    const queryMode = params.get("mode");
    return queryMode === "register" ? "register" : "login";
  }, [location.search]);

  useEffect(() => {
    setMode(initialModeFromQuery);
    setError("");
    setSuccessMessage("");
    setPassword("");
    setRepeatPassword("");
  }, [initialModeFromQuery]);

  useEffect(() => {
    if (!imgUrl) {
      setImgPreviewError(false);
      return;
    }

    setImgPreviewError(false);
  }, [imgUrl]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccessMessage("");

    if (mode === "login") {
      if (!username || !password) {
        setError("Introduce usuario y contraseña");
        return;
      }
    } else {
      if (!username || !password || !repeatPassword || !nombre || !email) {
        setError("Introduce todos los campos requeridos");
        return;
      }

      if (password !== repeatPassword) {
        setError("Las contraseñas no coinciden");
        return;
      }
    }

    setLoading(true);
    try {
      // 1) Get CSRF token + set cookie (SessionAuthentication)
      const csrfRes = await fetch("/api/auth/csrf/", {
        method: "GET",
        credentials: "include",
      });
      if (!csrfRes.ok) {
        throw new Error("No se pudo obtener el token CSRF");
      }
      const { csrfToken } = await csrfRes.json();

      if (mode === "login") {
        // 2) Login
        const loginRes = await fetch("/api/auth/login/", {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
          body: JSON.stringify({ username, password }),
        });

        const data = await loginRes.json().catch(() => ({}));
        if (!loginRes.ok) {
          throw new Error(data.detail || "Credenciales inválidas");
        }

        navigate("/inicio")

        return;
      }

      // 2) Register
      const registerRes = await fetch("/api/auth/register/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          username,
          nombre,
          password,
          imagen: imgUrl,
          email: email,
        }),
      });

      const data = await registerRes.json().catch(() => ({}));
      if (!registerRes.ok) {
        throw new Error(formatApiError(data) || "No se pudo registrar el usuario");
      }

      setSuccessMessage("Registro correcto. Ya puedes iniciar sesión.");
      setPassword("");
      setRepeatPassword("");
      setMode("login");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error en la autenticación");
    } finally {
      setLoading(false);
    }
  }

  function switchMode(nextMode) {
    setMode(nextMode);
    setError("");
    setSuccessMessage("");
    setPassword("");
    setRepeatPassword("");
    setImgUrl("");
  }

  return (
    <div className="app">
      <h1>M A T A C A R T A S</h1>

      <h2 className="">{mode === "login" ? "INICIO DE SESIÓN" : "REGISTRO"}</h2>

      <form onSubmit={handleSubmit}>
        <div style={{ marginTop: 12 }}>
          <label htmlFor="username">{mode === "login" ? "Usuario" : "Nombre de usuario *"}</label>
          <br />
          <input
            id="username"
            name="username"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loading}
          />
        </div>

        {mode === "register" && (
        <div style={{ marginTop: 12 }}>
          <label htmlFor="nombre">Nombre del perfil *</label>
          <br />
          <input
            id="nombre"
            name="nombre"
            autoComplete="nombre"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            disabled={loading}
          />
        </div>
        )}

        <div style={{ marginTop: 12 }}>
          <label htmlFor="password">{mode === "login" ? "Contraseña" : "Contraseña *"}</label>
          <br />
          <input
            id="password"
            name="password"
            type="password"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
          />
        </div>

        {mode === "register" && (
          <div style={{ marginTop: 12 }}>
            <label htmlFor="repeatPassword">Repetir contraseña *</label>
            <br />
            <input
              id="repeatPassword"
              name="repeatPassword"
              type="password"
              autoComplete="new-password"
              value={repeatPassword}
              onChange={(e) => setRepeatPassword(e.target.value)}
              disabled={loading}
            />
          </div>
        )}

        {mode === "register" && (
          <div style={{ marginTop: 12 }}>
            <label htmlFor="email">Correo electrónico *</label>
            <br />
            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            />
          </div>
        )}

        {mode === "register" && (
          <div style={{ marginTop: 12 }}>
            <label htmlFor="imgUrl">Foto de perfil</label>
            <div className="profile-preview" aria-hidden="true">
              <img
                className="profile-preview__img"
                src={profilePreviewSrc}
                alt="Previsualización de foto de perfil"
                onError={() => {
                  if (imgUrl) setImgPreviewError(true);
                }}
              />
            </div>
            <input
              id="imgUrl"
              name="imgUrl"
              type="url"
              placeholder="https://..."
              value={imgUrl}
              onChange={(e) => setImgUrl(e.target.value)}
              disabled={loading}
            />
            <p
              className={`profile-preview__warning ${
                showProfilePreviewWarning ? "" : "profile-preview__warning--hidden"
              }`}
              role="status"
              aria-live="polite"
              aria-hidden={!showProfilePreviewWarning}
            >
              {profilePreviewWarningText}
            </p>
          </div>
        )}

        <div style={{ marginTop: 12 }}>
          <button type="submit" disabled={loading}>
            {loading
              ? mode === "login"
                ? "Entrando..."
                : "Registrando..."
              : mode === "login"
                ? "Entrar"
                : "Registrarse"}
          </button>

          {mode === "login" ? (
            <button
              type="button"
              disabled={loading}
              style={{ marginLeft: 8 }}
              onClick={() => switchMode("register")}
            >
              Registrarse
            </button>
          ) : (
            <button
              type="button"
              disabled={loading}
              style={{ marginLeft: 8 }}
              onClick={() => switchMode("login")}
            >
              Volver a login
            </button>
          )}
        </div>

        {error && (
          <p role="alert" style={{ marginTop: 12, whiteSpace: "pre-line" }}>
            {error}
          </p>
        )}
        {successMessage && <p style={{ marginTop: 12 }}>{successMessage}</p>}
      </form>
    </div>
  );
}
