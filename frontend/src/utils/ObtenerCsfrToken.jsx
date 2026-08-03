
export async function obtenerCsrfToken() {
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

	return csrfToken;
}
