const DiccionarioTicketsFront = {
  ticket_cb_aleatorio: {
    nombre: "Cambio de baraja: aleatoria",
    clase: "2ª clase",
    descripcion: "Cambia la baraja por una nueva. Utilizar este ticket hará que todos los jugadores pierdan sus cartas y reciban nuevas. Sólo se puede usar durante serie de cambios, en la fase previa a los cambios de cartas.",
  },
  ticket_cb_con_unicas: {
    nombre: "Cambio baraja: con únicas",
    clase: "2ª clase",
    descripcion: "Cambia la baraja por una nueva, garantizando la presencia de, al menos, una carta única. Utilizar este ticket hará que todos los jugadores pierdan sus cartas y reciban nuevas. Sólo se puede usar durante serie de cambios, en la fase previa a los cambios de cartas.",
  },
  ticket_cb_valiosa: {
    nombre: "Cambio baraja: la valiosa",
    clase: "2ª clase",
    descripcion: "Cambia la baraja por una nueva, solo que las 12 cartas especiales son valiosas. Utilizar este ticket hará que todos los jugadores pierdan sus cartas y reciban nuevas. Sólo se puede usar durante serie de cambios, en la fase previa a los cambios de cartas.",
  },
  ticket_cb_magica: {
    nombre: "Cambio baraja: la mágica",
    clase: "1ª clase",
    descripcion: "Cambia la baraja por una nueva, garantizando 8 cartas valiosas y 6 cartas mágicas. Utilizar este ticket hará que todos los jugadores pierdan sus cartas y reciban nuevas. Sólo se puede usar durante serie de cambios, en la fase previa a los cambios de cartas.",
  },
  ticket_cb_unica: {
    nombre: "Cambio baraja: la única",
    clase: "1ª clase",
    descripcion: "Cambia la baraja por una nueva, garantizando 8 cartas valiosas, 4 cartas mágicas y 2 cartas únicas. Utilizar este ticket hará que todos los jugadores pierdan sus cartas y reciban nuevas. Sólo se puede usar durante serie de cambios, en la fase previa a los cambios de cartas.",
  },
  ticket_cb_todas: {
    nombre: "Cambio baraja: sólo especiales",
    clase: "Clase Imperial",
    descripcion: "Cambia la baraja por una nueva en la cual las 48 cartas son de tipo especial. Utilizar este ticket hará que todos los jugadores pierdan sus cartas y reciban nuevas. Sólo se puede usar durante serie de cambios, en la fase previa a los cambios de cartas.",
  },

  ticket_ic_azar: {
    nombre: "Intercambio de comodín: al azar",
    clase: "3ª clase",
    descripcion: "Intercambia tu comodín por el de un jugador seleccionado al azar. Este ticket sólo se puede utilizar durante la primera, segunda o tercera ronda.",
  },
  ticket_ic_primero: {
    nombre: "Intercambio de comodín: al primero",
    clase: "2ª clase",
    descripcion: "Intercambia tu comodín por el del jugador con más puntos. Este ticket sólo se puede utilizar durante la primera, segunda o tercera ronda.",
  },

  ticket_pp_2_azar: { nombre: "Pérdida de puntos: dos al azar", clase: "3ª clase", descripcion: "Hace perder 2 puntos a un jugador aleatorio." },
  ticket_pp_2_primero: { nombre: "Pérdida de puntos: dos al primero", clase: "2ª clase", descripcion: "Hace perder 2 puntos al jugador con más puntos." },
  ticket_pp_2_todos: { nombre: "Pérdida de puntos: dos a todos", clase: "2ª clase", descripcion: "Hace perder 2 puntos a todos los jugadores excepto al que utiliza el ticket." },
  ticket_pp_4_azar: { nombre: "Pérdida de puntos: cuatro al azar", clase: "2ª clase", descripcion: "Hace perder 4 puntos a un jugador aleatorio." },
  ticket_pp_4_primero: { nombre: "Pérdida de puntos: cuatro al primero", clase: "2ª clase", descripcion: "Hace perder 4 puntos al jugador con más puntos." },
  ticket_pp_4_todos: { nombre: "Pérdida de puntos: cuatro a todos", clase: "1ª clase", descripcion: "Hace perder 4 puntos a todos los jugadores excepto al que utiliza el ticket." },
  ticket_pp_6_azar: { nombre: "Pérdida de puntos: seis al azar", clase: "1ª clase", descripcion: "Hace perder 6 puntos a un jugador aleatorio." },
  ticket_pp_6_primero: { nombre: "Pérdida de puntos: seis al primero", clase: "1ª clase", descripcion: "Hace perder 6 puntos al jugador con más puntos." },
  ticket_pp_6_todos: { nombre: "Pérdida de puntos: seis a todos", clase: "Clase Imperial", descripcion: "Hace perder 6 puntos a todos los jugadores excepto al que utiliza el ticket." },

  ticket_rp_2_azar: { nombre: "Robo de puntos: al azar", clase: "2ª clase", descripcion: "Roba 2 puntos de un jugador al azar y se los otorga al que utiliza el ticket." },
  ticket_rp_2_primero: { nombre: "Robo de puntos: al primero", clase: "1ª clase", descripcion: "Roba 2 puntos del jugador con más puntos y se los otorga al que utiliza el ticket." },
  ticket_rp_2_todos: { nombre: "Robo de puntos: a todos", clase: "Clase Imperial", descripcion: "Roba 2 puntos de todos los jugadores y se los otorga al que utiliza el ticket." },

  ticket_cp_2: { nombre: "Canjear puntos: dos", clase: "3ª clase", descripcion: "Canjea el ticket por 2 puntos." },
  ticket_cp_4: { nombre: "Canjear puntos: cuatro", clase: "2ª clase", descripcion: "Canjea el ticket por 4 puntos." },
  ticket_cp_6: { nombre: "Canjear puntos: seis", clase: "1ª clase", descripcion: "Canjea el ticket por 6 puntos." },
  ticket_cp_10: { nombre: "Canjear puntos: diez", clase: "Clase Imperial", descripcion: "Canjea el ticket por 10 puntos." },

  ticket_ro_azar: { nombre: "Retirada forzada: al azar", clase: "3ª clase", descripcion: "Obliga a un jugador al azar a retirarse de la mano actual. Sólo puede utilizarse durante las rondas 1, 2 o 3." },
  ticket_ro_primero: { nombre: "Retirada forzada: al primero", clase: "2ª clase", descripcion: "Obliga al jugador con más puntos a retirarse de la mano actual. Sólo puede utilizarse durante las rondas 1, 2 o 3." },

  ticket_rt_azar: { nombre: "Robo de ticket: al azar", clase: "2ª clase", descripcion: "Roba el ticket de un jugador al azar y se lo da al que utiliza el ticket." },
  ticket_rt_primero: { nombre: "Robo de ticket: al primero", clase: "2ª clase", descripcion: "Roba un ticket del jugador con más puntos y se lo da al que utiliza el ticket." },
  ticket_rt_mayor_clase: { nombre: "Robo de ticket: mayor clase", clase: "Clase Imperial", descripcion: "Roba el ticket de mayor clase que haya en la mesa y se lo da al que utiliza el ticket." },
};

export default DiccionarioTicketsFront;
