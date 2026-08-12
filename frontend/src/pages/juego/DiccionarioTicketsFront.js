const DiccionarioTicketsFront = {
  ticket_cb_aleatorio: {
    nombre: "Cambio baraja aleatorio",
    clase: "2ª clase",
    descripcion: "Cambia la baraja de forma aleatoria aplicando un efecto de cambio.",
  },
  ticket_cb_con_unicas: {
    nombre: "Cambio baraja (con únicas)",
    clase: "2ª clase",
    descripcion: "Reordena la baraja privilegiando cartas únicas.",
  },
  ticket_cb_valiosa: {
    nombre: "Cambio baraja (valiosa)",
    clase: "2ª clase",
    descripcion: "Intercambia la baraja para favorecer cartas valiosas.",
  },
  ticket_cb_magica: {
    nombre: "Cambio baraja mágico",
    clase: "1ª clase",
    descripcion: "Efecto especial de cambio de baraja con resultados mágicos.",
  },
  ticket_cb_unica: {
    nombre: "Cambio baraja (única)",
    clase: "1ª clase",
    descripcion: "Cambia la baraja afectando sólo cartas únicas.",
  },
  ticket_cb_todas: {
    nombre: "Cambio baraja (todas)",
    clase: "Clase Imperial",
    descripcion: "Cambia la baraja usando todas las opciones disponibles.",
  },

  ticket_ic_azar: {
    nombre: "Intercambio comodín (azar)",
    clase: "3ª clase",
    descripcion: "Intercambia tu comodín por otro seleccionado al azar.",
  },
  ticket_ic_primero: {
    nombre: "Intercambio comodín (primero)",
    clase: "2ª clase",
    descripcion: "Intercambia tu comodín con el del primer jugador.",
  },

  ticket_pp_2_azar: { nombre: "Perdida 2 (azar)", clase: "3ª clase", descripcion: "Hace perder 2 puntos a un jugador aleatorio." },
  ticket_pp_2_primero: { nombre: "Perdida 2 (primero)", clase: "2ª clase", descripcion: "Hace perder 2 puntos al primer jugador." },
  ticket_pp_2_todos: { nombre: "Perdida 2 (todos)", clase: "2ª clase", descripcion: "Hace perder 2 puntos a todos los jugadores." },
  ticket_pp_4_azar: { nombre: "Perdida 4 (azar)", clase: "2ª clase", descripcion: "Hace perder 4 puntos a un jugador aleatorio." },
  ticket_pp_4_primero: { nombre: "Perdida 4 (primero)", clase: "2ª clase", descripcion: "Hace perder 4 puntos al primer jugador." },
  ticket_pp_4_todos: { nombre: "Perdida 4 (todos)", clase: "1ª clase", descripcion: "Hace perder 4 puntos a todos los jugadores." },
  ticket_pp_6_azar: { nombre: "Perdida 6 (azar)", clase: "1ª clase", descripcion: "Hace perder 6 puntos a un jugador aleatorio." },
  ticket_pp_6_primero: { nombre: "Perdida 6 (primero)", clase: "1ª clase", descripcion: "Hace perder 6 puntos al primer jugador." },
  ticket_pp_6_todos: { nombre: "Perdida 6 (todos)", clase: "Clase Imperial", descripcion: "Hace perder 6 puntos a todos los jugadores." },

  ticket_rp_2_azar: { nombre: "Robo 2 (azar)", clase: "2ª clase", descripcion: "Robas 2 puntos de un jugador aleatorio." },
  ticket_rp_2_primero: { nombre: "Robo 2 (primero)", clase: "1ª clase", descripcion: "Robas 2 puntos del primer jugador." },
  ticket_rp_2_todos: { nombre: "Robo 2 (todos)", clase: "Clase Imperial", descripcion: "Robas 2 puntos de todos los jugadores." },

  ticket_cp_2: { nombre: "Canje 2", clase: "3ª clase", descripcion: "Canjea el ticket por 2 puntos." },
  ticket_cp_4: { nombre: "Canje 4", clase: "2ª clase", descripcion: "Canjea el ticket por 4 puntos." },
  ticket_cp_6: { nombre: "Canje 6", clase: "1ª clase", descripcion: "Canjea el ticket por 6 puntos." },
  ticket_cp_10: { nombre: "Canje 10", clase: "Clase Imperial", descripcion: "Canjea el ticket por 10 puntos." },

  ticket_ro_azar: { nombre: "Retirada obligada (azar)", clase: "3ª clase", descripcion: "Obliga a retirar cartas de la mano a un jugador aleatorio." },
  ticket_ro_primero: { nombre: "Retirada obligada (primero)", clase: "2ª clase", descripcion: "Obliga al primer jugador a retirar cartas de su mano." },

  ticket_rt_azar: { nombre: "Robo ticket (azar)", clase: "2ª clase", descripcion: "Robas un ticket de un jugador aleatorio." },
  ticket_rt_primero: { nombre: "Robo ticket (primero)", clase: "2ª clase", descripcion: "Robas un ticket del primer jugador." },
  ticket_rt_mayor_clase: { nombre: "Robo ticket (mayor clase)", clase: "Clase Imperial", descripcion: "Robas el ticket de mayor clase de otro jugador." },
};

export default DiccionarioTicketsFront;
