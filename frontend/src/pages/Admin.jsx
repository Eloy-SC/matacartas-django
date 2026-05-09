import { useNavigate } from "react-router-dom";

export default function Admin() {
	const navigate = useNavigate();

	return (
		<div className="app">
			<h1>ADMINISTRACIÓN</h1>
			<button type="button" onClick={() => navigate("/admin/usuarios")}>
				Usuarios
			</button>
		</div>
	);
}
