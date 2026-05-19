import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import defaultProfilePic from "../../assets/default_profile_pic.png";
import "../../styles/admin.css";

export default function AdminUserForm() {
	const navigate = useNavigate();
	const { userId } = useParams();
	const mode = useMemo(() => (userId ? "edit" : "create"), [userId]);

	const [username, setUsername] = useState("");
	const [nombre, setNombre] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [repeatPassword, setRepeatPassword] = useState("");
	const [imgUrl, setImgUrl] = useState("");
	const [isStaff, setIsStaff] = useState(false);
	const [imgPreviewError, setImgPreviewError] = useState(false);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [successMessage, setSuccessMessage] = useState("");

	const profilePreviewSrc = imgUrl && !imgPreviewError ? imgUrl : defaultProfilePic;
	const showProfilePreviewWarning = Boolean(imgUrl) && imgPreviewError;
	const profilePreviewWarningText =
		"No se ha podido encontrar la imagen, se asignara esta por defecto";

	useEffect(() => {
		let cancelled = false;
		setError("");
		setSuccessMessage("");
		setImgPreviewError(false);

		if (!userId) return () => {};

		setLoading(true);
		fetch(`/api/users/admin/${userId}/`, { method: "GET", credentials: "include" })
			.then(async (res) => {
				const data = await res.json().catch(() => ({}));
				if (cancelled) return;
				if (!res.ok) {
					throw new Error(data?.detail || "No se pudo cargar el usuario");
				}
				setUsername(data?.username ?? "");
				setNombre(data?.nombre ?? "");
				setEmail(data?.email ?? "");
				setImgUrl(data?.imagen ?? "");
				setIsStaff(Boolean(data?.is_staff));
			})
			.catch((e) => {
				if (cancelled) return;
				setError(e instanceof Error ? e.message : "Error cargando usuario");
			})
			.finally(() => {
				if (cancelled) return;
				setLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, [userId]);

	async function handleSubmit(event) {
		event.preventDefault();
		setError("");
		setSuccessMessage("");

		if (!username || !nombre || !email) {
			setError("Introduce todos los campos requeridos");
			return;
		}

		if (password || repeatPassword) {
			if (!password || !repeatPassword) {
				setError("Introduce la contrasena y su repeticion");
				return;
			}
		}

		if (password && password !== repeatPassword) {
			setError("Las contrasenas no coinciden");
			return;
		}

		setLoading(true);
		try {
			const csrfRes = await fetch("/api/auth/csrf/", {
				method: "GET",
				credentials: "include",
			});
			if (!csrfRes.ok) {
				throw new Error("No se pudo obtener el token CSRF");
			}
			const { csrfToken } = await csrfRes.json();

			const payload = {
				username,
				nombre,
				email,
				imagen: imgUrl,
				is_staff: isStaff,
			};
			if (password) {
				payload.password = password;
			}

			const endpoint = userId
				? `/api/users/admin/${userId}/editar/`
				: "/api/users/admin/crear/";
			const method = userId ? "PUT" : "POST";
			const res = await fetch(endpoint, {
				method,
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
				body: JSON.stringify(payload),
			});

			const data = await res.json().catch(() => ({}));
			if (!res.ok) {
				const detail = data?.detail || "No se pudo guardar el usuario";
				throw new Error(detail);
			}

			setSuccessMessage(userId ? "Usuario actualizado" : "Usuario creado");
			navigate("/admin/usuarios");
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error guardando usuario");
		} finally {
			setLoading(false);
		}
	}

	return (
		<div className="app">
			<div className="admin-title-card">
				<h1 style={{ marginBottom: 0 }}>
					{mode === "edit" ? "ADMINISTRACION - EDITAR USUARIO" : "ADMINISTRACION - CREAR USUARIO"}
				</h1>
			</div>
			<div className="admin-form-card">
				<form onSubmit={handleSubmit}>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="username">Nombre de usuario *</label>
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
					<div style={{ marginTop: 12 }}>
						<label htmlFor="password">Contrasena {mode === "edit" ? "" : "*"}</label>
						<br />
						<input
							id="password"
							name="password"
							type="password"
							autoComplete="new-password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							disabled={loading}
						/>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="repeatPassword">Repetir contrasena {mode === "edit" ? "" : "*"}</label>
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
					<div style={{ marginTop: 12 }}>
						<label htmlFor="email">Correo electronico *</label>
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
					<div style={{ marginTop: 12 }}>
						<label htmlFor="isStaff">Administrador</label>
						<br />
						<input
							id="isStaff"
							name="isStaff"
							type="checkbox"
							className="admin-checkbox"
							checked={isStaff}
							onChange={(e) => setIsStaff(e.target.checked)}
							disabled={loading}
						/>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="imgUrl">Foto de perfil</label>
						<div className="profile-preview" aria-hidden="true">
							<img
								className="profile-preview__img"
								src={profilePreviewSrc}
								alt="Previsualizacion de foto de perfil"
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
					<div style={{ marginTop: 12 }}>
						<button type="submit" className="admin-primary-button">
							{mode === "edit" ? "Guardar cambios" : "Crear usuario"}
						</button>
						<button
							type="button"
							className="admin-secondary-button"
							onClick={() => navigate("/admin/usuarios")}
							style={{ marginLeft: 8 }}
							disabled={loading}
						>
							Volver
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
