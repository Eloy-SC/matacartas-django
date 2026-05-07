import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import defaultProfilePic from "../assets/default_profile_pic.png";

export default function Inicio() {
	const navigate = useNavigate();
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [profileImageUrl, setProfileImageUrl] = useState("");
	const [avatarError, setAvatarError] = useState(false);

	const avatarSrc = profileImageUrl && !avatarError ? profileImageUrl : defaultProfilePic;

	useEffect(() => {
		let cancelled = false;
		setAvatarError(false);

		fetch("/api/auth/me/", { method: "GET", credentials: "include" })
			.then((res) => res.json())
			.then((data) => {
				if (cancelled) return;
				const imagen = data?.perfil?.imagen;
				setProfileImageUrl(typeof imagen === "string" ? imagen : "");
			})
			.catch(() => {
				if (cancelled) return;
				setProfileImageUrl("");
			});

		return () => {
			cancelled = true;
		};
	}, []);

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
		<div className="app app--with-avatar">
			<button
				type="button"
				className="avatar-button"
				onClick={() => navigate("/perfil")}
				aria-label="Ir al perfil"
			>
				<img
					className="avatar-img"
					src={avatarSrc}
					alt="Foto de perfil"
					onError={() => {
						if (profileImageUrl) setAvatarError(true);
					}}
				/>
			</button>
			<h1>M A T A C A R T A S</h1>
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
