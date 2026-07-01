import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/admin.css";
import UserRango from "../../utils/UserRango.jsx";

const ORDER_FIELDS = [
  { value: "username", label: "Nombre de usuario" },
  { value: "nombre", label: "Nombre de perfil" },
  { value: "email", label: "Correo electrónico" },
  { value: "puntuacion", label: "Puntuación" },
  { value: "is_active", label: "Baneado" },
  { value: "is_staff", label: "Administrador" },
];

export default function AdminUsers() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [rangos, setRangos] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [selectedRango, setSelectedRango] = useState("");
  const [isActiveFilter, setIsActiveFilter] = useState("");
  const [isStaffFilter, setIsStaffFilter] = useState("");
  const [orderBy, setOrderBy] = useState("username");
  const [orderDir, setOrderDir] = useState("asc");

  const loadRangos = useCallback(() => {
    let cancelled = false;

    fetch("/api/rangos/listar/", {
      method: "GET",
      credentials: "include",
    })
      .then(async (res) => {
        const data = await res.json().catch(() => []);
        if (cancelled) return;
        if (!res.ok) {
          throw new Error(data?.detail || "No se pudo cargar la lista de rangos");
        }
        setRangos(Array.isArray(data) ? data : []);
      })
      .catch(() => {
        if (cancelled) return;
        setRangos([]);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const loadUsers = useCallback(
    (pageNumber = 1) => {
    let cancelled = false;
    setLoading(true);
    setError("");

    const params = new URLSearchParams();
    params.set("page", String(pageNumber));
    if (debouncedSearch.trim()) {
      params.set("search", debouncedSearch.trim());
    }
    if (selectedRango) {
      params.set("rango_id", selectedRango);
    }
    if (isActiveFilter) {
      params.set("is_active", isActiveFilter);
    }
    if (isStaffFilter) {
      params.set("is_staff", isStaffFilter);
    }
    if (orderBy) {
      const orderingValue = orderDir === "desc" ? `-${orderBy}` : orderBy;
      params.set("ordering", orderingValue);
    }

    fetch(`/api/users/admin/listar/?${params.toString()}`, {
      method: "GET",
      credentials: "include",
    })
      .then(async (res) => {
        const data = await res.json().catch(() => ({}));
        if (cancelled) return;
        if (!res.ok) {
          const detail = data?.detail || "No se pudo cargar la lista de usuarios";
          throw new Error(detail);
        }
        const items = Array.isArray(data?.items) ? data.items : [];

        if (cancelled) return;
        setUsers(items);
        setPage(typeof data?.page === "number" ? data.page : pageNumber);
        setTotalPages(typeof data?.total_pages === "number" ? data.total_pages : 1);
        setTotalUsers(typeof data?.total === "number" ? data.total : 0);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : "Error cargando usuarios");
        setUsers([]);
        setTotalUsers(0);
        setTotalPages(1);
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
    },
    [
      debouncedSearch,
      selectedRango,
      isActiveFilter,
      isStaffFilter,
      orderBy,
      orderDir,
    ]
  );

  useEffect(() => {
    const cancel = loadRangos();
    return () => {
      if (typeof cancel === "function") cancel();
    };
  }, [loadRangos]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setDebouncedSearch(search);
    }, 300);
    return () => {
      clearTimeout(timeoutId);
    };
  }, [search]);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, selectedRango, isActiveFilter, isStaffFilter, orderBy, orderDir]);

  useEffect(() => {
    const cancel = loadUsers(page);
    return () => {
      if (typeof cancel === "function") cancel();
    };
  }, [loadUsers, page]);

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

      const res = await fetch(`/api/users/admin/${userId}/eliminar/`, {
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

      loadUsers(page);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error eliminando usuario");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="app">
      <button className="admin-volver-button" onClick={() => navigate("/admin")}>
        ⮜
      </button>
      <div className="admin-title-card">
        <h1 style={{ marginBottom: 0 }}>ADMINISTRACIÓN - USUARIOS</h1>
      </div>
      <div className="admin-toolbar-card">
        <input
          type="search"
          className="admin-search-input"
          placeholder="Buscar usuario..."
          aria-label="Buscar usuario"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          disabled={loading}
        />
        <select
          className="admin-search-input"
          value={selectedRango}
          onChange={(e) => setSelectedRango(e.target.value)}
          aria-label="Filtrar por rango"
          disabled={loading}
        >
          <option value="">Todos los rangos</option>
          {rangos.map((rango) => (
            <option key={rango.id ?? rango.nombre} value={rango.id ?? ""}>
              {rango.nombre ?? ""}
            </option>
          ))}
        </select>
        <select
          className="admin-search-input"
          value={isActiveFilter}
          onChange={(e) => setIsActiveFilter(e.target.value)}
          aria-label="Filtrar por baneado"
          disabled={loading}
        >
          <option value="">Todos</option>
          <option value="false">Baneados</option>
          <option value="true">No baneados</option>
        </select>
        <select
          className="admin-search-input"
          value={isStaffFilter}
          onChange={(e) => setIsStaffFilter(e.target.value)}
          aria-label="Filtrar por administrador"
          disabled={loading}
        >
          <option value="">Todos</option>
          <option value="true">Administradores</option>
          <option value="false">No administradores</option>
        </select>
        <select
          className="admin-search-input"
          value={orderBy}
          onChange={(e) => setOrderBy(e.target.value)}
          aria-label="Ordenar por"
          disabled={loading}
        >
          {ORDER_FIELDS.map((field) => (
            <option key={field.value} value={field.value}>
              Ordenar: {field.label}
            </option>
          ))}
        </select>
        <select
          className="admin-search-input"
          value={orderDir}
          onChange={(e) => setOrderDir(e.target.value)}
          aria-label="Ordenar direccion"
          disabled={loading}
        >
          <option value="asc">Ascendente</option>
          <option value="desc">Descendente</option>
        </select>
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
        <p role="alert" style={{ fontWeight: "bold", color: "white" }}>
          {error}
        </p>
      ) : (
        <div className="admin-users-table-wrap">
          <table className="admin-users-table">
            <thead>
              <tr>
                <th>Nombre de usuario</th>
                <th>Nombre de perfil</th>
                <th>Correo electrónico</th>
                <th>Rango</th>
                <th>Puntuación</th>
                <th>Baneado</th>
                <th>Administrador</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan={8}>No hay usuarios.</td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id ?? user.username}>
                    <td>{user.username ?? ""}</td>
                    <td>{user.nombre ?? ""}</td>
                    <td>{user.email ?? ""}</td>
                    <td>
                      <UserRango userId={user.id} />
                    </td>
                    <td>{typeof user.puntuacion === "number" ? user.puntuacion : ""}</td>
                    <td>{user.is_active ? "❌" : "🟩"}</td>
                    <td>{user.is_staff ? "🟩" : "❌"}</td>
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
                          disabled={loading || deletingId === user.id || user.is_staff}
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
          <div className="admin-pagination">
            <button
              type="button"
              className="admin-secondary-button"
              onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              disabled={loading || page <= 1}
            >
              Anterior
            </button>
            <span className="admin-pagination__info">
              Pagina {page} de {totalPages} ({totalUsers} usuarios)
            </span>
            <button
              type="button"
              className="admin-secondary-button"
              onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
              disabled={loading || page >= totalPages}
            >
              Siguiente
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
