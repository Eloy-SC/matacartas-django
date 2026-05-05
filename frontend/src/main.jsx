import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Inicio from "./pages/Inicio.jsx";
import "./index.css";

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

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/inicio"
          element={
            <RequireAuth>
              <Inicio />
            </RequireAuth>
          }
        />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
