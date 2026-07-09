
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function Juego() {
  const { partidaId } = useParams();
	const [mesa, setMesa] = useState(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	const partida = mesa?.partida ?? null;
	const mano = mesa?.mano ?? null;
	const jugador = mesa?.jugador ?? null;
	const contrincantes = mesa?.contrincantes ?? [];
	const rondas = mesa?.rondas ?? [];
	const puedeRepartir =
		jugador?.color &&
		Array.isArray(partida?.disposicion_jugadores) &&
		partida.disposicion_jugadores.at(-1) === jugador.color;

	const formatCartas = (cartas) => {
		if (Array.isArray(cartas)) {
			return cartas.join(", ");
		}

		if (typeof cartas === "string") {
			return cartas;
		}

		if (cartas && typeof cartas === "object") {
			return Object.entries(cartas)
				.map(([clave, valor]) => `${clave}: ${valor}`)
				.join(", ");
		}

		return "";
	};

	const loadMesa = async ({ showLoading = true } = {}) => {
		if (showLoading) {
			setLoading(true);
			setError("");
		}

		try {
			const res = await fetch(`/api/partida/${partidaId}/mano/mesa/`, {
				method: "GET",
				credentials: "include",
			});

			const data = await res.json().catch(() => ({}));

			if (!res.ok) {
				throw new Error(data?.detail || "No se pudo cargar la mesa");
			}

			setMesa(data);
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error cargando la mesa");
			setMesa(null);
		} finally {
			if (showLoading) {
				setLoading(false);
			}
		}
	};

	const handleRepartirCartas = async () => {
		try {
			const csrfRes = await fetch("/api/auth/csrf/", {
				method: "GET",
				credentials: "include",
			});

			if (!csrfRes.ok) {
				throw new Error("No se pudo obtener el token CSRF");
			}

			const { csrfToken } = await csrfRes.json().catch(() => ({}));

			if (!csrfToken) {
				throw new Error("Token CSRF no disponible");
			}

			const repartirRes = await fetch(`/api/partida/${partidaId}/mano/repartir/`, {
				method: "PUT",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
			});

			const repartirData = await repartirRes.json().catch(() => ({}));

			if (!repartirRes.ok) {
				throw new Error(repartirData?.detail || "Error repartiendo cartas");
			}

			await loadMesa({ showLoading: false });
		} catch (e) {
			alert(
				e instanceof Error
					? e.message
					: "Error repartiendo cartas"
			);
		}
	};

	useEffect(() => {
		void loadMesa({ showLoading: true });
	}, [partidaId]);

	useEffect(() => {
		const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
		let socket;
		let reconnectTimer;
		let shouldReconnect = true;

		const connect = () => {
			socket = new WebSocket(
				`${protocol}//${window.location.host}/ws/partidas/${partidaId}/mesa/`
			);

			socket.onopen = () => {
				console.log("WS conectado");
			};

			socket.onmessage = async (event) => {
				const data = JSON.parse(event.data);

				if (data.type === "mesa_updated") {
					await loadMesa({ showLoading: false });
				}
			};

			socket.onclose = () => {
				if (!shouldReconnect) {
					return;
				}

				console.log("WS cerrado, reintentando...");
				reconnectTimer = setTimeout(connect, 3000);
			};
		};

		connect();

		return () => {
			shouldReconnect = false;
			clearTimeout(reconnectTimer);
			socket?.close();
		};
	}, [partidaId]);

  return (
    <div className="juego-container">
      <h1>Juego</h1>
			{loading ? (
				<p>Cargando mesa...</p>
			) : error ? (
				<p role="alert">{error}</p>
			) : (
				<div className="juego-mesa">
					<section className="juego-mesa__bloque">
						<h2>Partida</h2>
						<p>Identificador: {partida?.partida_id ?? "-"}</p>
						<p>Cartas en la baraja: {partida?.baraja_cant ?? "-"}</p>
						<p>Disposición de jugadores: {partida?.disposicion_jugadores?.join(", ") ?? "-"}</p>
						<p>Turno actual: {partida?.turno_actual ?? "-"}</p>
						<p>Tiempo máximo de turno: {partida?.tiempo_max_turno ?? "-"} s</p>
					</section>

					<section className="juego-mesa__bloque">
						<h2>Mano</h2>
						<p>Identificador: {mano?.mano_id ?? "-"}</p>
						<p>Número de mano: {mano?.mano_num ?? "-"}</p>
					</section>

					<section className="juego-mesa__bloque">
						<h2>Tu jugador</h2>
						<p>Identificador: {jugador?.jugador_id ?? "-"}</p>
						<p>Nombre: {jugador?.nombre ?? "-"}</p>
						<p>Color: {jugador?.color ?? "-"}</p>
						<p>Puntos: {jugador?.puntos ?? "-"}</p>
						<p>Cartas: {jugador?.cartas}</p>
						<p>Carta comodín: {jugador?.carta_comodin ?? "-"}</p>
					</section>

					<section className="juego-mesa__bloque">
						<h2>Contrincantes</h2>
						{contrincantes.length === 0 ? (
							<p>No hay contrincantes cargados.</p>
						) : (
							<ul>
								{contrincantes.map((contrincante) => (
									<li key={contrincante.contrincante_id}>
										{contrincante.nombre} - {contrincante.puntos} puntos - {contrincante.cartas_cant} cartas - comodín: {contrincante.carta_comodin ? "Sí" : "No"}
									</li>
								))}
							</ul>
						)}
					</section>

					<section className="juego-mesa__bloque">
						<h2>Rondas</h2>
						{rondas.length === 0 ? (
							<p>No hay rondas cargadas.</p>
						) : (
							<ul>
								{rondas.map((ronda) => (
									<li key={ronda.ronda_id}>
										Ronda {ronda.ronda_num}: {formatCartas(ronda.cartas) || "sin cartas"}
									</li>
								))}
							</ul>
						)}
					</section>
				</div>
			)}

		{puedeRepartir && (
			<button
				type="button"
				className="main-primary-button"
						onClick={handleRepartirCartas}
				aria-label="Repartir cartas"
			>
				Repartir cartas
			</button>
		)}
    </div>
  );
}