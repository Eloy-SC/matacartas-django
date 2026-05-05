import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Inicio() {
	const navigate = useNavigate();
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");

	async function handleLogout() {
		setLoading(true);
		setError("");
		try {
			const csrfRes = await fetch("/api/auth/csrf/", {
				method: "GET",
				credentials: "include",
			});
			if (!csrfRes.ok) {
				throw new Error("No se pudo obtener el token CSRF");
			}
			const { csrfToken } = await csrfRes.json();

			const logoutRes = await fetch("/api/auth/logout/", {
				method: "POST",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
			});
			if (!logoutRes.ok) {
				const data = await logoutRes.json().catch(() => ({}));
				throw new Error(data.detail || "No se pudo cerrar sesión");
			}

			navigate("/login", { replace: true });
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error cerrando sesión");
		} finally {
			setLoading(false);
		}
	}

	return (
		<div className="app">
			<h1>Inicio</h1>
			<p>Esta es una página protegida: sólo accesible si has iniciado sesión.</p>
			<button type="button" onClick={handleLogout} disabled={loading}>
				{loading ? "Cerrando sesión..." : "Cerrar sesión"}
			</button>
			{error && (
				<p role="alert" style={{ marginTop: 12 }}>
					{error}
				</p>
			)}
		</div>
	);
}
