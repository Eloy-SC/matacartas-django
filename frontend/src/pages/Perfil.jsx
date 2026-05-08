import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import defaultProfilePic from "../assets/default_profile_pic.png";

export default function Perfil() {
	const navigate = useNavigate();
	const [loading, setLoading] = useState(true);
	const [saving, setSaving] = useState(false);
	const [error, setError] = useState("");
	const [editing, setEditing] = useState(false);
	const [avatarError, setAvatarError] = useState(false);

	const [me, setMe] = useState(null);
	const [form, setForm] = useState({
		username: "",
		email: "",
		nombre: "",
		imagen: "",
	});
	const [newPassword, setNewPassword] = useState("");
	const [repeatNewPassword, setRepeatNewPassword] = useState("");

	const puntuacion = me?.perfil?.puntuacion ?? "";
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
				nombre: data?.perfil?.nombre ?? "",
				imagen: data?.perfil?.imagen ?? "",
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
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	function startEdit() {
		setError("");
		setEditing(true);
		setNewPassword("");
		setRepeatNewPassword("");
		setAvatarError(false);
	}

	function cancelEdit() {
		setError("");
		setEditing(false);
		setNewPassword("");
		setRepeatNewPassword("");
		setForm({
			username: me?.username ?? "",
			email: me?.email ?? "",
			nombre: me?.perfil?.nombre ?? "",
			imagen: me?.perfil?.imagen ?? "",
		});
		setAvatarError(false);
	}

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

			setEditing(false);
			setNewPassword("");
			setRepeatNewPassword("");
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
				<h1>M A T A C A R T A S</h1>
				<h2>PERFIL</h2>
				<p>Cargando...</p>
			</div>
		);
	}

	return (
		<div className="app app--with-avatar">
			<button
				type="button"
				className="avatar-button"
				onClick={() => navigate("/inicio")}
				aria-label="Volver a inicio"
			>
				<img
					className="avatar-img"
					src={avatarSrc}
					alt="Foto de perfil"
					onError={() => {
						if (form.imagen) setAvatarError(true);
					}}
				/>
			</button>

			<h1>M A T A C A R T A S</h1>
			<h2>PERFIL</h2>

			<div className="profile-preview">
				<img
					className="profile-preview__img"
					src={avatarSrc}
					alt="Vista previa de la imagen"
					onError={() => {
						if (form.imagen) setAvatarError(true);
					}}
				/>
			</div>

			<form onSubmit={handleSave} style={{ width: "min(420px, 100%)" }}>
				<div style={{ display: "grid", gap: 10 }}>
					<div style={{ display: "grid", gap: 6 }}>
						<label htmlFor="perfil-username">Username</label>
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
						<label htmlFor="perfil-email">Email</label>
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
						<label htmlFor="perfil-nombre">Nombre</label>
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

					<div style={{ display: "grid", gap: 6 }}>
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
								avatarError ? "profile-preview__warning" : "profile-preview__warning profile-preview__warning--hidden"
							}
						>
							No se pudo cargar la imagen; se muestra la predeterminada.
						</p>
					</div>

					<div style={{ display: "grid", gap: 6 }}>
						<label htmlFor="perfil-puntuacion">Puntuación</label>
						<input id="perfil-puntuacion" value={String(puntuacion ?? "")} readOnly />
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

				<div style={{ display: "flex", gap: 10, marginTop: 14, justifyContent: "center" }}>
					{editing ? (
						<>
							<button type="submit" disabled={saving}>
								{saving ? "Guardando..." : "Guardar"}
							</button>
							<button type="button" onClick={cancelEdit} disabled={saving}>
								Cancelar
							</button>
						</>
					) : (
						<>
							<button type="button" onClick={startEdit}>
								Editar
							</button>
							<button type="button" onClick={() => navigate("/inicio")}>
								Volver
							</button>
						</>
					)}
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
