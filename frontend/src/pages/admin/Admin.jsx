import { useNavigate } from "react-router-dom";

export default function Admin() {
	const navigate = useNavigate();

	return (
		<div className="app">
			<button className="admin-volver-button" onClick={() => navigate("/inicio")}>
				⮜
			</button>
			<div className="admin-title-card">
				<h1 style={{ marginBottom: 0 }}>ADMINISTRACIÓN</h1>
			</div>
			<div className="admin-form-card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
				<button type="button" className="admin-primary-button" onClick={() => navigate("/admin/usuarios")}>
					USUARIOS
				</button>
				<button type="button" className="admin-primary-button" onClick={() => navigate("/admin/rangos")}>
					RANGOS
				</button>
			</div>
		</div>
	);
}
