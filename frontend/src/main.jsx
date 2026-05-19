import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Inicio from "./pages/Inicio.jsx";
import Perfil from "./pages/Perfil.jsx";
import Admin from "./pages/admin/Admin.jsx";
import AdminUsers from "./pages/admin/AdminUsers.jsx";
import AdminUserForm from "./pages/admin/AdminUserForm.jsx";
import AdminRangos from "./pages/admin/AdminRangos.jsx";
import AdminRangoForm from "./pages/admin/AdminRangoForm.jsx";
import "./index.css";
import "./styles/main.css";

function RequireAuth({ children }) {
  const location = useLocation();
  const [status, setStatus] = React.useState("checking"); // checking | authed | unauthed

  React.useEffect(() => {
    let cancelled = false;

    fetch("/api/auth/me/", { method: "GET", credentials: "include" })
      .then((res) => {
        if (cancelled) return;
        setStatus(res.ok ? "authed" : "unauthed");
      })
      .catch(() => {
        if (cancelled) return;
        setStatus("unauthed");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "checking") return null;
  if (status === "unauthed") {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}

function RequireAdmin({ children }) {
  const location = useLocation();
  const [status, setStatus] = React.useState("checking"); // checking | staff | no-staff

  React.useEffect(() => {
    let cancelled = false;

    fetch("/api/auth/me/", { method: "GET", credentials: "include" })
      .then(async (res) => {
        if (cancelled) return;
        if (!res.ok) {
          setStatus("no-staff");
          return;
        }
        const data = await res.json().catch(() => ({}));
        setStatus(Boolean(data?.is_staff) ? "staff" : "no-staff");
      })
      .catch(() => {
        if (cancelled) return;
        setStatus("no-staff");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "checking") return null;
  if (status === "no-staff") {
    return <Navigate to="/inicio" replace state={{ from: location }} />;
  }

  return children;
}

function RedirectIfAuthed({ children }) {
  const [status, setStatus] = React.useState("checking"); // checking | authed | unauthed

  React.useEffect(() => {
    let cancelled = false;

    fetch("/api/auth/me/", { method: "GET", credentials: "include" })
      .then((res) => {
        if (cancelled) return;
        setStatus(res.ok ? "authed" : "unauthed");
      })
      .catch(() => {
        if (cancelled) return;
        setStatus("unauthed");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "checking") return null;
  if (status === "authed") {
    return <Navigate to="/inicio" replace />;
  }

  return children;
}


ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={ <RedirectIfAuthed> <App /> </RedirectIfAuthed>} />
        <Route path="/login" element={ <RedirectIfAuthed> <Login /> </RedirectIfAuthed>} />

        {/* Necesario iniciar sesión */}
        <Route path="/inicio" element={ <RequireAuth> <Inicio /> </RequireAuth>}/>
        <Route path="/perfil" element={ <RequireAuth> <Perfil /> </RequireAuth>}/>

        {/* Necesario ser administrador */}
        <Route path="/admin" element={ <RequireAdmin> <Admin /> </RequireAdmin>}/>
        <Route path="/admin/usuarios" element={ <RequireAdmin> <AdminUsers /> </RequireAdmin>}/>
        <Route path="/admin/usuarios/crear" element={ <RequireAdmin> <AdminUserForm /> </RequireAdmin>}/>
        <Route path="/admin/usuarios/:userId" element={ <RequireAdmin> <AdminUserForm /> </RequireAdmin>}/>
        <Route path="/admin/rangos" element={ <RequireAdmin> <AdminRangos /> </RequireAdmin>}/>
        <Route path="/admin/rangos/crear" element={ <RequireAdmin> <AdminRangoForm /> </RequireAdmin>}/>
        <Route path="/admin/rangos/:rangoId" element={ <RequireAdmin> <AdminRangoForm /> </RequireAdmin>}/>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
