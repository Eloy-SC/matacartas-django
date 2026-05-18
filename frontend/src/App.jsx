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
        <div>
          <button type="button" className="app-inicio-button" onClick={() => navigate("/login")}> 
            INICIA SESIÓN
          </button>
        </div>
        <div>
          <button type="button" className="app-inicio-button" onClick={() => navigate("/login?mode=register")}>
            REGÍSTRATE
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
