import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [apiStatus, setApiStatus] = useState(null);

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
      {apiStatus && (
        <div className={`api-status ${apiStatus.status}`}>
          <strong>API Status:</strong> {apiStatus.message}
        </div>
      )}
    </div>
  );
}

export default App;
