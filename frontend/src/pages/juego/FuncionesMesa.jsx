import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";

export function formatCartas(cartas) {
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
}

export async function handleRepartirCartas(partidaId, loadMesa) {
	try {
		const csrfToken = await obtenerCsrfToken();

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
}

export async function handleEleccionCambio(partidaId, accion, loadMesa) {
	try {
		const csrfToken = await obtenerCsrfToken();

		const cambioRes = await fetch(`/api/partida/${partidaId}/mano/${accion}/`, {
			method: "PUT",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": csrfToken,
			},
		});

		const cambioData = await cambioRes.json().catch(() => ({}));

		if (!cambioRes.ok) {
			throw new Error(cambioData?.detail || "Error registrando la decisión de cambio");
		}

		await loadMesa({ showLoading: false });
	} catch (e) {
		alert(e instanceof Error ? e.message : "Error registrando la decisión de cambio");
	}
}

export async function handleEleccionComodin(partidaId, cartaComodin, loadMesa) {
	if (!cartaComodin) {
		alert("Selecciona una carta para elegirla como comodín.");
		return;
	}

	try {
		const csrfToken = await obtenerCsrfToken();

		const comodinRes = await fetch(`/api/partida/${partidaId}/mano/elegir-carta-comodin/`, {
			method: "PUT",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": csrfToken,
			},
			body: JSON.stringify({ carta_comodin: cartaComodin }),
		});

		const comodinData = await comodinRes.json().catch(() => ({}));

		if (!comodinRes.ok) {
			throw new Error(comodinData?.detail || "Error eligiendo carta comodín");
		}

		await loadMesa({ showLoading: false });
	} catch (e) {
		alert(e instanceof Error ? e.message : "Error eligiendo carta comodín");
	}
}

export async function handleJugarCarta(partidaId, carta, loadMesa) {
	if (!carta) {
		return null;
	}

	try {
		const csrfToken = await obtenerCsrfToken();

		const jugarRes = await fetch(`/api/partida/${partidaId}/mano/ronda/jugar-carta/`, {
			method: "PUT",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": csrfToken,
			},
			body: JSON.stringify({ carta }),
		});

		const jugarData = await jugarRes.json().catch(() => ({}));

		if (!jugarRes.ok) {
			throw new Error(jugarData?.detail || "Error jugando la carta");
		}

		await loadMesa({ showLoading: false });
		return jugarData;
	} catch (e) {
		alert(e instanceof Error ? e.message : "Error jugando la carta");
		return null;
	}
}

export async function handleRetirarseDeMano(partidaId, loadMesa) {
	try {
		const csrfToken = await obtenerCsrfToken();

		const retirarseRes = await fetch(`/api/partida/${partidaId}/mano/ronda/retirarse/`, {
			method: "PUT",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": csrfToken,
			},
		});

		const retirarseData = await retirarseRes.json().catch(() => ({}));

		if (!retirarseRes.ok) {
			throw new Error(retirarseData?.detail || "Error retirándose de la mano");
		}

		await loadMesa({ showLoading: false });
		return retirarseData;
	} catch (e) {
		alert(e instanceof Error ? e.message : "Error retirándose de la mano");
		return null;
	}
}

export async function handleSiguienteMano(partidaId, loadMesa) {
	try {
		const csrfToken = await obtenerCsrfToken();

		const siguienteManoRes = await fetch(`/api/partida/${partidaId}/mano/siguiente-mano/`, {
			method: "POST",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": csrfToken,
			},
		});

		const siguienteManoData = await siguienteManoRes.json().catch(() => ({}));

		if (!siguienteManoRes.ok) {
			throw new Error(siguienteManoData?.detail || "Error iniciando la siguiente mano");
		}

		await loadMesa({ showLoading: false });
		return siguienteManoData;
	} catch (e) {
		alert(e instanceof Error ? e.message : "Error iniciando la siguiente mano");
		return null;
	}
}

export async function handleCambiarCartas(partidaId, cartasSeleccionadas, loadMesa, setCartasSeleccionadas) {
	if (cartasSeleccionadas.length === 0) {
		alert("Selecciona al menos una carta para cambiar.");
		return;
	}

	try {
		const csrfToken = await obtenerCsrfToken();

		const cambioRes = await fetch(`/api/partida/${partidaId}/mano/cambiar-cartas/`, {
			method: "PUT",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": csrfToken,
			},
			body: JSON.stringify({ cartas: cartasSeleccionadas }),
		});

		const cambioData = await cambioRes.json().catch(() => ({}));

		if (!cambioRes.ok) {
			throw new Error(cambioData?.detail || "Error cambiando cartas");
		}

		setCartasSeleccionadas([]);
		await loadMesa({ showLoading: false });
	} catch (e) {
		alert(e instanceof Error ? e.message : "Error cambiando cartas");
	}
}

export function handleToggleCartaSeleccionada(puedeCambiarCartas, setCartasSeleccionadas, carta) {
	if (!puedeCambiarCartas) {
		return;
	}

	setCartasSeleccionadas((cartasActuales) =>
		cartasActuales.includes(carta)
			? cartasActuales.filter((cartaSeleccionada) => cartaSeleccionada !== carta)
			: [...cartasActuales, carta]
	);
}

export function handleToggleCartaSeleccionadaUnica(puedeSeleccionar, setCartaSeleccionada, carta) {
	if (!puedeSeleccionar) {
		return;
	}

	setCartaSeleccionada((cartaActual) => (cartaActual === carta ? null : carta));
}
