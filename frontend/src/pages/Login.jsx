import { useState } from "react";

export default function Login() {
  const [mode, setMode] = useState("login"); // 'login' | 'register'
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccessMessage("");

    if (!username || !password) {
      setError("Introduce usuario y contraseña");
      return;
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

        setSuccessMessage("Login correcto");
        setPassword("");
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
        body: JSON.stringify({ username, password }),
      });

      const data = await registerRes.json().catch(() => ({}));
      if (!registerRes.ok) {
        throw new Error(data.detail || "No se pudo registrar el usuario");
      }

      setSuccessMessage("Registro correcto. Ya puedes iniciar sesión.");
      setPassword("");
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
  }

  return (
    <div className="app">
      <h1>{mode === "login" ? "Login" : "Registro"}</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="username">Usuario</label>
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

        <div style={{ marginTop: 12 }}>
          <label htmlFor="password">Contraseña</label>
          <br />
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
          />
        </div>

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
          <p role="alert" style={{ marginTop: 12 }}>
            {error}
          </p>
        )}
        {successMessage && <p style={{ marginTop: 12 }}>{successMessage}</p>}
      </form>
    </div>
  );
}
