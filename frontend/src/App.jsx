import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./App.css";

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
      <h1>Matacartas</h1>
      <p>Django + React + PostgreSQL starter app</p>
      <button type="button" onClick={() => navigate("/login")}> 
        Ir a login
      </button>
      {apiStatus && (
        <div className={`api-status ${apiStatus.status}`}>
          <strong>API Status:</strong> {apiStatus.message}
        </div>
      )}
    </div>
  );
}

export default App;
