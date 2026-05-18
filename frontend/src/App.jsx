import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./App.css";
import cabecera from "./assets/cabecera.png";

function App() {
  const [apiStatus, setApiStatus] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/api/health/")
      .then((res) => res.json())
      .then((data) => setApiStatus(data))
      .catch(() => setApiStatus({ status: "error", message: "Could not connect to API" }));
  }, []);

  return (
    <div className="app">
      <img src={cabecera} alt="Matacartas" style={{maxWidth: "100%", height: "auto"}} />
      <div>
        <button type="button" onClick={() => navigate("/login")}> 
          Ir a login
        </button>
        <button
          type="button"
          style={{ marginLeft: 8 }}
          onClick={() => navigate("/login?mode=register")}
        >
          Registrarse
        </button>
      </div>
    </div>
  );
}

export default App;
