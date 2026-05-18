import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/admin.css";

export default function AdminUsers() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  const loadUsers = useCallback(() => {
    let cancelled = false;
    setLoading(true);
    setError("");

    fetch("/api/users/admin/listar/", { method: "GET", credentials: "include" })
      .then(async (res) => {
        const data = await res.json().catch(() => []);
        if (cancelled) return;
        if (!res.ok) {
          const detail = data?.detail || "No se pudo cargar la lista de usuarios";
          throw new Error(detail);
        }
        setUsers(Array.isArray(data) ? data : []);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : "Error cargando usuarios");
        setUsers([]);
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const cancel = loadUsers();
    return () => {
      if (typeof cancel === "function") cancel();
    };
  }, [loadUsers]);

  async function handleDelete(userId) {
    if (!userId || deletingId) return;
    const ok = window.confirm("¿Seguro que quieres eliminar este usuario?");
    if (!ok) return;

    setDeletingId(userId);
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

      const res = await fetch(`/api/users/admin/${userId}/`, {
        method: "DELETE",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data?.detail || "No se pudo eliminar el usuario");
      }

      loadUsers();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error eliminando usuario");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="app">
      <div className="admin-title-card">
        <h1 style={{ marginBottom: 0 }}>ADMINISTRACIÓN - USUARIOS</h1>
      </div>
      <div className="admin-toolbar-card">
        <input
          type="search"
          className="admin-search-input"
          placeholder="Buscar usuario..."
          aria-label="Buscar usuario"
          disabled={loading}
        />
        <button
          type="button"
          className="admin-primary-button"
          onClick={() => navigate("/admin/usuarios/crear")}
          disabled={loading}
        >
          Crear usuario
        </button>
      </div>
      {loading ? (
        <p style={{ fontWeight: "bold", color: "white" }}>Cargando...</p>
      ) : error ? (
        <p role="alert">{error}</p>
      ) : (
        <div className="admin-users-table-wrap">
          <table className="admin-users-table">
            <thead>
              <tr>
                <th>Nombre de usuario</th>
                <th>Nombre de perfil</th>
                <th>Correo electrónico</th>
                <th>Activo</th>
                <th>Administrador</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan={6}>No hay usuarios.</td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id ?? user.username}>
                    <td>{user.username ?? ""}</td>
                    <td>{user.nombre ?? ""}</td>
                    <td>{user.email ?? ""}</td>
                    <td>{user.is_active ? "Si" : "No"}</td>
                    <td>{user.is_staff ? "Si" : "No"}</td>
                    <td>
                      <div className="admin-actions">
                        <button
                          type="button"
                          className="admin-icon-button"
                          aria-label="Editar usuario"
                          onClick={() => navigate(`/admin/usuarios/${user.id}`)}
                          disabled={loading || deletingId === user.id}
                        >
                          <svg
                            viewBox="0 0 24 24"
                            role="img"
                            aria-hidden="true"
                            className="admin-icon"
                          >
                            <path d="M3 17.25V21h3.75L19.81 7.94l-3.75-3.75L3 17.25zm2.92 2.33H5v-.92l9.06-9.06.92.92L5.92 19.58zM20.71 6.04a1 1 0 0 0 0-1.41L19.37 3.3a1 1 0 0 0-1.41 0l-1.09 1.09 3.75 3.75 1.09-1.1z" />
                          </svg>
                        </button>
                        <button
                          type="button"
                          className="admin-delete-button"
                          aria-label="Borrar usuario"
                          onClick={() => handleDelete(user.id)}
                          disabled={loading || deletingId === user.id}
                        >
                          <svg
                            viewBox="0 0 24 24"
                            role="img"
                            aria-hidden="true"
                            className="admin-icon"
                          >
                            <path d="M9 3h6l1 1h4v2H4V4h4l1-1zm1 6h2v9h-2V9zm4 0h2v9h-2V9zM7 9h2v9H7V9zm-1 12h12a1 1 0 0 0 1-1V8H5v12a1 1 0 0 0 1 1z" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
              ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
