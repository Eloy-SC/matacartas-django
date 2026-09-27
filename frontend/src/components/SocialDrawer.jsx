import { useEffect, useState } from "react";
import defaultProfilePic from "../assets/default_profile_pic.png";
import UserRango from "../utils/UserRango.jsx";
import { obtenerCsrfToken } from "../utils/ObtenerCsfrToken";
import "../styles/social_drawer.css";

export default function SocialDrawer({ canInviteToMatch = false, partidaId = null }) {
	const [isOpen, setIsOpen] = useState(false);
	const [activeSection, setActiveSection] = useState("notifications");
	const [friends, setFriends] = useState([]);
	const [friendsPage, setFriendsPage] = useState(1);
	const [friendsTotalPages, setFriendsTotalPages] = useState(1);
	const [friendsSearch, setFriendsSearch] = useState("");
	const [friendsSearchInput, setFriendsSearchInput] = useState("");
	const [friendsLoading, setFriendsLoading] = useState(false);
	const [friendsError, setFriendsError] = useState("");
	const [invitingFriendId, setInvitingFriendId] = useState(null);

	useEffect(() => {
		if (!isOpen || activeSection !== "friends") return;

		let cancelled = false;
		setFriendsLoading(true);
		setFriendsError("");

		const params = new URLSearchParams({
			page: String(friendsPage),
		});
		if (friendsSearch) params.set("search", friendsSearch);

		fetch(`/api/amigos/listar/?${params.toString()}`, {
			method: "GET",
			credentials: "include",
		})
			.then(async (res) => {
				const data = await res.json().catch(() => ({}));
				if (!res.ok) throw new Error(data?.detail || "No se pudieron cargar los amigos");
				if (cancelled) return;
				setFriends(Array.isArray(data?.items) ? data.items : []);
				setFriendsTotalPages(Math.max(1, Number(data?.total_pages) || 1));
			})
			.catch((error) => {
				if (cancelled) return;
				setFriends([]);
				setFriendsError(error instanceof Error ? error.message : "Error cargando amigos");
			})
			.finally(() => {
				if (!cancelled) setFriendsLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, [activeSection, friendsPage, friendsSearch, isOpen]);

	function handleFriendsSearch(event) {
		event.preventDefault();
		setFriendsPage(1);
		setFriendsSearch(friendsSearchInput.trim());
	}

	async function handleInvite(friendId) {
		if (!partidaId || invitingFriendId !== null) return;

		setInvitingFriendId(friendId);
		try {
			const csrfToken = await obtenerCsrfToken();
			const response = await fetch(
				`/api/notificaciones/invitacion-partida/enviar/${friendId}/${partidaId}/`,
				{
					method: "POST",
					credentials: "include",
					headers: { "X-CSRFToken": csrfToken },
				}
			);
			const data = await response.json().catch(() => ({}));
			if (!response.ok) throw new Error(data?.detail || "No se pudo enviar la invitación");

			setFriends((currentFriends) =>
				currentFriends.map((friend) =>
					friend.id === friendId ? { ...friend, invitado: true } : friend
				)
			);
		} catch (error) {
			setFriendsError(error instanceof Error ? error.message : "Error enviando la invitación");
		} finally {
			setInvitingFriendId(null);
		}
	}

	return (
		<>
			<button
				type="button"
				className="social-drawer-trigger"
				onClick={() => setIsOpen(true)}
				aria-label="Abrir notificaciones y amigos"
				aria-expanded={isOpen}
			>
				<span aria-hidden="true">◧</span>
			</button>

			{isOpen && (
				<div className="social-drawer-layer">
					<button
						type="button"
						className="social-drawer-backdrop"
						onClick={() => setIsOpen(false)}
						aria-label="Cerrar panel"
					/>
					<aside className="social-drawer" aria-label="Panel social">
						<header className="social-drawer__header">
							<div>
								<span className="social-drawer__eyebrow">Comunidad</span>
								<h2>Panel social</h2>
							</div>
							<button
								type="button"
								className="social-drawer__close"
								onClick={() => setIsOpen(false)}
								aria-label="Cerrar panel social"
							>
								×
							</button>
						</header>

						<nav className="social-drawer__tabs" aria-label="Secciones del panel social">
							<button
								type="button"
								className={activeSection === "notifications" ? "is-active" : ""}
								onClick={() => setActiveSection("notifications")}
								aria-pressed={activeSection === "notifications"}
							>
								Notificaciones
							</button>
							<button
								type="button"
								className={activeSection === "friends" ? "is-active" : ""}
								onClick={() => {
									setFriendsPage(1);
									setActiveSection("friends");
								}}
								aria-pressed={activeSection === "friends"}
							>
								Amigos
							</button>
						</nav>

						<section className="social-drawer__content" aria-live="polite">
							{activeSection === "notifications" ? (
								<>
									<h3>Notificaciones</h3>
									<p>Aquí aparecerán tus notificaciones.</p>
								</>
							) : (
								<>
									<h3>Amigos</h3>
									<form className="social-drawer__search" onSubmit={handleFriendsSearch}>
										<label htmlFor="social-friends-search">Buscar amigo</label>
										<div>
											<input
												id="social-friends-search"
												value={friendsSearchInput}
												onChange={(event) => setFriendsSearchInput(event.target.value)}
												placeholder="Nombre"
											/>
											<button type="submit" aria-label="Buscar amigo">Buscar</button>
										</div>
									</form>
									{friendsLoading ? (
										<p>Cargando amigos...</p>
									) : friendsError ? (
										<p className="social-drawer__error" role="alert">{friendsError}</p>
									) : friends.length === 0 ? (
										<p>No se encontraron amigos.</p>
									) : (
										<div className="social-drawer__friends">
											{friends.map((friend) => (
												<article className="social-friend" key={friend.id}>
													<img
														className="social-friend__avatar"
														src={friend.imagen || defaultProfilePic}
														alt={`Foto de perfil de ${friend.nombre || "amigo"}`}
														onError={(event) => { event.currentTarget.src = defaultProfilePic; }}
													/>
													<div className="social-friend__details">
														<strong>{friend.nombre || "Sin nombre"}</strong>
														<UserRango userId={friend.id} />
													</div>
													{canInviteToMatch && (
														friend.invitado ? (
															<span className="social-friend__invited">Invitación enviada</span>
														) : (
															<button
																type="button"
																className="social-friend__invite"
																onClick={() => handleInvite(friend.id)}
																disabled={invitingFriendId === friend.id}
															>
																{invitingFriendId === friend.id ? "Enviando..." : "Invitar a la partida"}
															</button>
														)
													)}
												</article>
											))}
										</div>
									)}
									{friendsTotalPages > 1 && (
										<div className="social-drawer__pagination">
											<button type="button" onClick={() => setFriendsPage((page) => page - 1)} disabled={friendsPage <= 1} aria-label="Página anterior">‹</button>
											<span>Página {friendsPage} de {friendsTotalPages}</span>
											<button type="button" onClick={() => setFriendsPage((page) => page + 1)} disabled={friendsPage >= friendsTotalPages} aria-label="Página siguiente">›</button>
										</div>
									)}
								</>
							)}
						</section>
					</aside>
				</div>
			)}
		</>
	);
}