import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import defaultProfilePic from "../assets/default_profile_pic.png";

export default function Perfil() {
	const location = useLocation();
	const navigate = useNavigate();
	const [loading, setLoading] = useState(true);
	const [saving, setSaving] = useState(false);
	const [error, setError] = useState("");
	const [avatarError, setAvatarError] = useState(false);
	const [mode, setMode] = useState("view"); // 'view' | 'edit'

	const initialModeFromQuery = useMemo(() => {
		const params = new URLSearchParams(location.search);
		const queryMode = params.get("mode");
		return queryMode === "edit" ? "edit" : "view";
	}, [location.search]);

	useEffect(() => {
		setMode(initialModeFromQuery);
		setError("");
		setNewPassword("");
		setRepeatNewPassword("");
		setAvatarError(false);
	}, [initialModeFromQuery]);

	const editing = mode === "edit";

	function switchMode(nextMode) {
		setMode(nextMode);
		setError("");
		setNewPassword("");
		setRepeatNewPassword("");
		setAvatarError(false);
		if (nextMode === "view") {
			setForm({
				username: me?.username ?? "",
				email: me?.email ?? "",
				nombre: me?.nombre ?? "",
				imagen: me?.imagen ?? "",
			});
		}
		navigate(`/perfil?mode=${nextMode}`, { replace: true });
	}

	const [me, setMe] = useState(null);
	const [form, setForm] = useState({
		username: "",
		email: "",
		nombre: "",
		imagen: "",
	});
	const [newPassword, setNewPassword] = useState("");
	const [repeatNewPassword, setRepeatNewPassword] = useState("");

	const puntuacion = me?.puntuacion ?? "";
	const avatarSrc = useMemo(() => {
		const url = form.imagen?.trim();
		if (!url || avatarError) return defaultProfilePic;
		return url;
	}, [form.imagen, avatarError]);

	async function loadMe() {
		setLoading(true);
		setError("");
		try {
			const res = await fetch("/api/auth/me/", { method: "GET", credentials: "include" });
			const data = await res.json().catch(() => ({}));
			if (!res.ok) {
				throw new Error(data?.detail || "No se pudo cargar el perfil");
			}

			setMe(data);
			setForm({
				username: data?.username ?? "",
				email: data?.email ?? "",
				nombre: data?.nombre ?? "",
				imagen: data?.imagen ?? "",
			});
			setAvatarError(false);
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error cargando el perfil");
		} finally {
			setLoading(false);
		}
	}

	useEffect(() => {
		let cancelled = false;
		(async () => {
			if (cancelled) return;
			await loadMe();
		})();
		return () => {
			cancelled = true;
		};
	}, []);

	async function handleSave(e) {
		e.preventDefault();
		if (saving) return;

		setError("");
		const nextPassword = newPassword.trim();
		const nextPassword2 = repeatNewPassword.trim();
		if ((nextPassword || nextPassword2) && nextPassword !== nextPassword2) {
			setError("Las contraseñas no coinciden");
			return;
		}

		setSaving(true);
		try {
			const csrfRes = await fetch("/api/auth/csrf/", {
				method: "GET",
				credentials: "include",
			});
			if (!csrfRes.ok) {
				throw new Error("No se pudo obtener el token CSRF");
			}
			const { csrfToken } = await csrfRes.json();

			const imagenValue = (form.imagen ?? "").trim();
			const payload = {
				username: (form.username ?? "").trim(),
				email: (form.email ?? "").trim(),
				nombre: (form.nombre ?? "").trim(),
				imagen: imagenValue ? imagenValue : null,
			};
			if (nextPassword) {
				payload.password = nextPassword;
			}

			const res = await fetch("/api/users/perfil/actualizar/", {
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
				const msg =
					(data && typeof data === "object" &&
						(Object.values(data)
							.flat()
							.filter((v) => typeof v === "string")
							.at(0) ||
							data.detail)) ||
					"No se pudo actualizar el perfil";
				throw new Error(msg);
			}

			// Si se cambió la contraseña, forzamos cierre de sesión y mandamos a login.
			if (nextPassword) {
				try {
					await fetch("/api/auth/logout/", {
						method: "POST",
						credentials: "include",
						headers: {
							"Content-Type": "application/json",
							"X-CSRFToken": csrfToken,
						},
					});
				} finally {
					navigate("/login", { replace: true });
				}
				return;
			}

			switchMode("view");
			await loadMe();
		} catch (e2) {
			setError(e2 instanceof Error ? e2.message : "Error actualizando el perfil");
		} finally {
			setSaving(false);
		}
	}

	if (loading) {
		return (
			<div className="app">
				<h1 style={{ marginBottom: 60 }}>PERFIL</h1>
				<p>Cargando...</p>
			</div>
		);
	}

	return (
		<div className="app">
			<h1 style={{ marginBottom: 40 }}>PERFIL</h1>

			<form
				onSubmit={handleSave}
				style={{ width: "min(900px, 100%)", margin: "0 auto" }}
			>
				<div style={{ display: "flex", gap: 24, alignItems: "flex-start", flexWrap: "wrap" }}>
					<div style={{ width: 420 }}>
						<div className="profile-preview" style={{ width: 420, height: 420 }}>
							<img
								className="profile-preview__img"
								src={avatarSrc}
								alt="Vista previa de la imagen"
								onError={() => {
									if (form.imagen) setAvatarError(true);
								}}
								style={{ width: 420, height: 420, objectFit: "cover" }}
							/>
						</div>

						<div style={{ display: "grid", gap: 6, marginTop: 10 }}>
							<label htmlFor="perfil-imagen">Imagen (URL)</label>
							{editing ? (
								<input
									id="perfil-imagen"
									value={form.imagen ?? ""}
									onChange={(e3) => {
										setAvatarError(false);
										setForm((prev) => ({ ...prev, imagen: e3.target.value }));
									}}
									placeholder="https://..."
								/>
							) : (
								<input id="perfil-imagen" value={form.imagen ?? ""} readOnly />
							)}
							<p
								className={
									avatarError
										? "profile-preview__warning"
										: "profile-preview__warning profile-preview__warning--hidden"
								}
							>
								No se puede obtener la imagen; se te asignará la predeterminada.
							</p>
						</div>
					</div>

					<div style={{ flex: 1, minWidth: 260 }}>
						<div style={{ display: "flex", gap: 10, marginBottom: 14, justifyContent: "center" }}>
							{editing ? (
								<>
									<button type="submit" disabled={saving}>
										{saving ? "Guardando..." : "Guardar"}
									</button>
									<button
										type="button"
										onClick={(e) => {
											e.preventDefault();
											e.stopPropagation();
											switchMode("view");
										}}
										disabled={saving}
									>
										Cancelar
									</button>
								</>
							) : (
								<>
									<button
										type="button"
										onClick={(e) => {
											e.preventDefault();
											e.stopPropagation();
											switchMode("edit");
										}}
									>
										Editar
									</button>
									<button type="button" onClick={() => navigate("/inicio")}>
										Volver
									</button>
								</>
							)}
						</div>

						<div style={{ display: "flex", gap: 10, marginBottom: 30, marginTop: 30, justifyContent: "center" }}>
							<h3>Puntuación: {puntuacion}</h3>
						</div>

						<div style={{ display: "grid", gap: 10 }}>
							<div style={{ display: "grid", gap: 6 }}>
								<label htmlFor="perfil-username">Nombre de usuario</label>
								{editing ? (
									<input
										id="perfil-username"
										value={form.username}
										onChange={(e3) => setForm((prev) => ({ ...prev, username: e3.target.value }))}
										autoComplete="username"
										required
									/>
								) : (
									<input id="perfil-username" value={form.username} readOnly />
								)}
							</div>

							<div style={{ display: "grid", gap: 6 }}>
								<label htmlFor="perfil-email">Correo electrónico</label>
								{editing ? (
									<input
										id="perfil-email"
										type="email"
										value={form.email}
										onChange={(e3) => setForm((prev) => ({ ...prev, email: e3.target.value }))}
										autoComplete="email"
										required
									/>
								) : (
									<input id="perfil-email" type="email" value={form.email} readOnly />
								)}
							</div>

							<div style={{ display: "grid", gap: 6 }}>
								<label htmlFor="perfil-nombre">Nombre de perfil</label>
								{editing ? (
									<input
										id="perfil-nombre"
										value={form.nombre}
										onChange={(e3) => setForm((prev) => ({ ...prev, nombre: e3.target.value }))}
										required
									/>
								) : (
									<input id="perfil-nombre" value={form.nombre} readOnly />
								)}
							</div>

							{editing && (
								<>
									<div style={{ display: "grid", gap: 6 }}>
										<label htmlFor="perfil-pass1">Nueva contraseña</label>
										<input
											id="perfil-pass1"
											type="password"
											value={newPassword}
											onChange={(e3) => setNewPassword(e3.target.value)}
											autoComplete="new-password"
										/>
									</div>
									<div style={{ display: "grid", gap: 6 }}>
										<label htmlFor="perfil-pass2">Repetir nueva contraseña</label>
										<input
											id="perfil-pass2"
											type="password"
											value={repeatNewPassword}
											onChange={(e3) => setRepeatNewPassword(e3.target.value)}
											autoComplete="new-password"
										/>
									</div>
								</>
							)}
						</div>
					</div>
				</div>
			</form>

			{error && (
				<p role="alert" style={{ marginTop: 12 }}>
					{error}
				</p>
			)}
		</div>
	);
}
