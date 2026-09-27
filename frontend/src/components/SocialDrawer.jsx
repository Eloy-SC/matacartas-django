import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import defaultProfilePic from "../assets/default_profile_pic.png";
import UserRango from "../utils/UserRango.jsx";
import { obtenerCsrfToken } from "../utils/ObtenerCsfrToken";
import "../styles/social_drawer.css";

export default function SocialDrawer({ canInviteToMatch = false, partidaId = null, partidaPlayerIds = [] }) {
	const navigate = useNavigate();
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
	const [friendsView, setFriendsView] = useState("list");
	const [users, setUsers] = useState([]);
	const [usersPage, setUsersPage] = useState(1);
	const [usersTotalPages, setUsersTotalPages] = useState(1);
	const [usersSearch, setUsersSearch] = useState("");
	const [usersSearchInput, setUsersSearchInput] = useState("");
	const [usersLoading, setUsersLoading] = useState(false);
	const [usersError, setUsersError] = useState("");
	const [addingUserId, setAddingUserId] = useState(null);
	const [removingFriendId, setRemovingFriendId] = useState(null);
	const [notifications, setNotifications] = useState([]);
	const [notificationsPage, setNotificationsPage] = useState(1);
	const [notificationsTotalPages, setNotificationsTotalPages] = useState(1);
	const [notificationsLoading, setNotificationsLoading] = useState(false);
	const [notificationsError, setNotificationsError] = useState("");
	const [processingNotificationId, setProcessingNotificationId] = useState(null);

	useEffect(() => {
		if (!isOpen || activeSection !== "notifications") return;

		let cancelled = false;
		setNotificationsLoading(true);
		setNotificationsError("");

		fetch(`/api/notificaciones/listar/?page=${notificationsPage}`, {
			method: "GET",
			credentials: "include",
		})
			.then(async (res) => {
				const data = await res.json().catch(() => ({}));
				if (!res.ok) throw new Error(data?.detail || "No se pudieron cargar las notificaciones");
				if (cancelled) return;
				setNotifications(Array.isArray(data?.items) ? data.items : []);
				setNotificationsTotalPages(Math.max(1, Number(data?.total_pages) || 1));
			})
			.catch((error) => {
				if (cancelled) return;
				setNotifications([]);
				setNotificationsError(error instanceof Error ? error.message : "Error cargando notificaciones");
			})
			.finally(() => {
				if (!cancelled) setNotificationsLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, [activeSection, isOpen, notificationsPage]);

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

	useEffect(() => {
		if (!isOpen || activeSection !== "friends" || friendsView !== "add") return;

		let cancelled = false;
		setUsersLoading(true);
		setUsersError("");

		const params = new URLSearchParams({ page: String(usersPage) });
		if (usersSearch) params.set("search", usersSearch);

		fetch(`/api/usuarios/buscar-amistad/?${params.toString()}`, {
			method: "GET",
			credentials: "include",
		})
			.then(async (res) => {
				const data = await res.json().catch(() => ({}));
				if (!res.ok) throw new Error(data?.detail || "No se pudieron cargar los usuarios");
				if (cancelled) return;
				setUsers(Array.isArray(data?.items) ? data.items : []);
				setUsersTotalPages(Math.max(1, Number(data?.total_pages) || 1));
			})
			.catch((error) => {
				if (cancelled) return;
				setUsers([]);
				setUsersError(error instanceof Error ? error.message : "Error buscando usuarios");
			})
			.finally(() => {
				if (!cancelled) setUsersLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, [activeSection, friendsView, isOpen, usersPage, usersSearch]);

	function handleFriendsSearch(event) {
		event.preventDefault();
		setFriendsPage(1);
		setFriendsSearch(friendsSearchInput.trim());
	}

	function handleUsersSearch(event) {
		event.preventDefault();
		setUsersPage(1);
		setUsersSearch(usersSearchInput.trim());
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

	async function handleAddUser(userId) {
		if (addingUserId !== null) return;

		setAddingUserId(userId);
		try {
			const csrfToken = await obtenerCsrfToken();
			const response = await fetch(`/api/notificaciones/solicitud-amistad/enviar/${userId}/`, {
				method: "POST",
				credentials: "include",
				headers: { "X-CSRFToken": csrfToken },
			});
			const data = await response.json().catch(() => ({}));
			if (!response.ok) throw new Error(data?.detail || "No se pudo enviar la solicitud de amistad");

			setUsers((currentUsers) =>
				currentUsers.map((user) => user.id === userId ? { ...user, agregado: true } : user)
			);
		} catch (error) {
			setUsersError(error instanceof Error ? error.message : "Error enviando la solicitud");
		} finally {
			setAddingUserId(null);
		}
	}

	async function handleRemoveFriend(friendId, friendName) {
		if (!window.confirm(`¿Seguro que quieres eliminar a ${friendName || "este amigo"} como amigo?`)) {
			return;
		}

		setRemovingFriendId(friendId);
		try {
			const csrfToken = await obtenerCsrfToken();
			const response = await fetch(`/api/amigos/${friendId}/eliminar/`, {
				method: "DELETE",
				credentials: "include",
				headers: { "X-CSRFToken": csrfToken },
			});
			const data = await response.json().catch(() => ({}));
			if (!response.ok) throw new Error(data?.detail || "No se pudo eliminar al amigo");

			setFriends((currentFriends) => currentFriends.filter((friend) => friend.id !== friendId));
		} catch (error) {
			setFriendsError(error instanceof Error ? error.message : "Error eliminando al amigo");
		} finally {
			setRemovingFriendId(null);
		}
	}

	async function handleNotificationAction(notification, action) {
		if (processingNotificationId !== null) return;

		setProcessingNotificationId(notification.id);
		setNotificationsError("");
		try {
			const csrfToken = await obtenerCsrfToken();
			const isFriendRequest = notification.tipo === "solicitud_amistad";
			const notificationBase = isFriendRequest
				? `/api/notificaciones/solicitud-amistad/${action}/${notification.id}/`
				: `/api/notificaciones/invitacion-partida/${action}/${notification.id}/`;
			const notificationResponse = await fetch(notificationBase, {
				method: action === "aceptar" ? "POST" : "DELETE",
				credentials: "include",
				headers: { "X-CSRFToken": csrfToken },
			});
			const notificationData = await notificationResponse.json().catch(() => ({}));
			if (!notificationResponse.ok) {
				throw new Error(notificationData?.detail || "No se pudo procesar la notificación");
			}

			if (!isFriendRequest && action === "aceptar") {
				if (canInviteToMatch && partidaId) {
					const leaveResponse = await fetch(`/api/partidas/${partidaId}/sala-espera/abandonar/`, {
						method: "DELETE",
						credentials: "include",
						headers: { "X-CSRFToken": csrfToken },
					});
					const leaveData = await leaveResponse.json().catch(() => ({}));
					if (!leaveResponse.ok) {
						throw new Error(leaveData?.detail || "No se pudo abandonar la sala actual");
					}
				}

				const joinResponse = await fetch(`/api/partidas/${notification.partida_id}/unirse/`, {
					method: "POST",
					credentials: "include",
					headers: { "X-CSRFToken": csrfToken },
				});
				const joinData = await joinResponse.json().catch(() => ({}));
				if (!joinResponse.ok) {
					throw new Error(joinData?.detail || "No se pudo unir a la partida");
				}

				navigate(`/partidas/sala-de-espera/${notification.partida_id}`);
			}

			setNotifications((currentNotifications) =>
				currentNotifications.filter((item) => item.id !== notification.id)
			);
		} catch (error) {
			setNotificationsError(error instanceof Error ? error.message : "Error procesando la notificación");
		} finally {
			setProcessingNotificationId(null);
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
									setFriendsView("list");
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
									{notificationsLoading ? (
										<p>Cargando notificaciones...</p>
									) : notificationsError ? (
										<p className="social-drawer__error" role="alert">{notificationsError}</p>
									) : notifications.length === 0 ? (
										<p>No tienes notificaciones.</p>
									) : (
										<div className="social-drawer__notifications">
											{notifications.map((notification) => {
												const isFriendRequest = notification.tipo === "solicitud_amistad";
												const isProcessing = processingNotificationId === notification.id;
												return (
													<article className="social-notification" key={`${notification.tipo}-${notification.id}`}>
														<div className="social-notification__identity">
															<img
																className="social-friend__avatar"
																src={notification.emisor_imagen || defaultProfilePic}
																alt={`Foto de perfil de ${notification.emisor_nombre || "usuario"}`}
																onError={(event) => { event.currentTarget.src = defaultProfilePic; }}
															/>
															<div>
																<strong>{isFriendRequest ? "Solicitud de amistad" : "Invitación a partida"}</strong>
																<span>de {notification.emisor_nombre || "usuario"}</span>
															</div>
														</div>
														<div className="social-notification__actions">
															<button type="button" onClick={() => handleNotificationAction(notification, "aceptar")} disabled={isProcessing}>
																{isProcessing ? "Procesando..." : "Aceptar"}
															</button>
															<button type="button" onClick={() => handleNotificationAction(notification, "rechazar")} disabled={isProcessing}>
																Rechazar
															</button>
														</div>
													</article>
												);
											})}
										</div>
									)}
									{notificationsTotalPages > 1 && (
										<div className="social-drawer__pagination">
											<button type="button" onClick={() => setNotificationsPage((page) => page - 1)} disabled={notificationsPage <= 1} aria-label="Página anterior">‹</button>
											<span>Página {notificationsPage} de {notificationsTotalPages}</span>
											<button type="button" onClick={() => setNotificationsPage((page) => page + 1)} disabled={notificationsPage >= notificationsTotalPages} aria-label="Página siguiente">›</button>
										</div>
									)}
								</>
							) : (
								<>
									{friendsView === "list" ? (
										<>
											<h3>Amigos</h3>
											<button
												type="button"
												className="social-drawer__add-friend"
												onClick={() => {
													setUsersPage(1);
													setFriendsView("add");
												}}
											>
												Agregar nuevo amigo
											</button>
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
																partidaPlayerIds.includes(friend.id) ? (
																	<span className="social-friend__invited">Ya está en la partida</span>
																) : friend.invitado ? (
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
															<button
																type="button"
																className="social-friend__remove"
																onClick={() => handleRemoveFriend(friend.id, friend.nombre)}
																disabled={removingFriendId === friend.id}
																aria-label={`Eliminar a ${friend.nombre || "amigo"}`}
																title="Eliminar amigo"
															>
																🗑
															</button>
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
									) : (
										<>
											<div className="social-drawer__subview-header">
												<h3>Agregar nuevo amigo</h3>
												<button type="button" onClick={() => setFriendsView("list")}>Volver</button>
											</div>
											<form className="social-drawer__search" onSubmit={handleUsersSearch}>
												<label htmlFor="social-users-search">Buscar usuario</label>
												<div>
													<input
														id="social-users-search"
														value={usersSearchInput}
														onChange={(event) => setUsersSearchInput(event.target.value)}
														placeholder="Nombre"
													/>
													<button type="submit" aria-label="Buscar usuario">Buscar</button>
												</div>
											</form>
											{usersLoading ? <p>Cargando usuarios...</p> : usersError ? (
												<p className="social-drawer__error" role="alert">{usersError}</p>
											) : users.length === 0 ? <p>No se encontraron usuarios.</p> : (
												<div className="social-drawer__friends">
													{users.map((user) => (
														<article className="social-friend" key={user.id}>
															<img
																className="social-friend__avatar"
																src={user.imagen || defaultProfilePic}
																alt={`Foto de perfil de ${user.nombre || "usuario"}`}
																onError={(event) => { event.currentTarget.src = defaultProfilePic; }}
															/>
															<div className="social-friend__details">
																<strong>{user.nombre || "Sin nombre"}</strong>
																<UserRango userId={user.id} />
															</div>
															{user.agregado ? (
																<span className="social-friend__invited">Solicitud de amistad enviada</span>
															) : (
																<button
																	type="button"
																	className="social-friend__invite"
																	onClick={() => handleAddUser(user.id)}
																	disabled={addingUserId === user.id}
																>
																	{addingUserId === user.id ? "Enviando..." : "Agregar"}
																</button>
															)}
														</article>
													))}
												</div>
											)}
											{usersTotalPages > 1 && (
												<div className="social-drawer__pagination">
													<button type="button" onClick={() => setUsersPage((page) => page - 1)} disabled={usersPage <= 1} aria-label="Página anterior">‹</button>
													<span>Página {usersPage} de {usersTotalPages}</span>
													<button type="button" onClick={() => setUsersPage((page) => page + 1)} disabled={usersPage >= usersTotalPages} aria-label="Página siguiente">›</button>
												</div>
											)}
										</>
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