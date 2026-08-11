TICKETS = {

    ###### TICKETS DE CAMBIO DE BARAJA ######
    "ticket_cb_aleatorio": {
        "seccion": "cambio_baraja",
        "clase": 2,
        "usable": "cambios",
    },
    "ticket_cb_con_unicas": {
        "seccion": "cambio_baraja",
        "clase": 2,
        "usable": "cambios",
    },
    "ticket_cb_valiosa": {
        "seccion": "cambio_baraja",
        "clase": 2,
        "usable": "cambios",
    },    
    "ticket_cb_magica": {
        "seccion": "cambio_baraja",
        "clase": 1,
        "usable": "cambios",
    },
    "ticket_cb_unica": {
        "seccion": "cambio_baraja",
        "clase": 1,
        "usable": "cambios",
    },
    "ticket_cb_todas": {
        "seccion": "cambio_baraja",
        "clase": 0,
        "usable": "cambios",
    },

    ###### TICKETS DE INTERCAMBIO DE COMODINES ######
    "ticket_ic_azar": {
        "seccion": "intercambio_comodin",
        "clase": 3,
        "usable": "general",
    },
    "ticket_ic_primero": {
        "seccion": "intercambio_comodin",
        "clase": 2,
        "usable": "general",
    },

    ###### TICKETS DE PERDIDA DE PUNTOS ######
    "ticket_pp_2_azar": {
        "seccion": "perdida_puntos",
        "clase": 3,
        "usable": "general",
    },
    "ticket_pp_2_primero": {
        "seccion": "perdida_puntos",
        "clase": 3,
        "usable": "general",
    },
    "ticket_pp_2_todos": {
        "seccion": "perdida_puntos",
        "clase": 2,
        "usable": "general",
    },    
    "ticket_pp_4_azar": {
        "seccion": "perdida_puntos",
        "clase": 2,
        "usable": "general",
    },
    "ticket_pp_4_primero": {
        "seccion": "perdida_puntos",
        "clase": 2,
    },
    "ticket_pp_4_todos": {
        "seccion": "perdida_puntos",
        "clase": 1,
        "usable": "general",
    },
    "ticket_pp_6_azar": {
        "seccion": "perdida_puntos",
        "clase": 1,
        "usable": "general",
    },
    "ticket_pp_6_primero": {
        "seccion": "perdida_puntos",
        "clase": 1,
        "usable": "general",
    },
    "ticket_pp_6_todos": {
        "seccion": "perdida_puntos",
        "clase": 0,
        "usable": "general",
    },

    ###### TICKETS DE ROBO DE PUNTOS ######
    "ticket_rp_2_azar": {
        "seccion": "robo_puntos",
        "clase": 2,
        "usable": "general",
    },
    "ticket_rp_2_primero": {
        "seccion": "robo_puntos",
        "clase": 1,
        "usable": "general",
    },
    "ticket_rp_2_todos": {
        "seccion": "robo_puntos",
        "clase": 0,
        "usable": "general",
    },

    ###### TICKETS CANJEABLES POR PUNTOS ######
    "ticket_cp_2": {
        "seccion": "canjeo_puntos",
        "clase": 3,
        "usable": "general",
    },
    "ticket_cp_4": {
        "seccion": "canjeo_puntos",
        "clase": 2,
        "usable": "general",
    },
    "ticket_cp_6": {
        "seccion": "canjeo_puntos",
        "clase": 1,
        "usable": "general",
    },
    "ticket_cp_10": {
        "seccion": "canjeo_puntos",
        "clase": 0,
        "usable": "general",
    },

    ###### TICKETS RETIRADA OBLIGADA DE MANO ######

    "ticket_ro_azar": {
        "seccion": "retirada_obligada",
        "clase": 3,
        "usable": "cambios",
    },
    "ticket_ro_primero": {
        "seccion": "retirada_obligada",
        "clase": 2,
        "usable": "cambios",
    },

    ###### TICKETS ROBO DE TICKET ######

    "ticket_rt_azar": {
        "seccion": "robo_ticket",
        "clase": 2,
        "usable": "cambios",
    },
    "ticket_rt_primero": {
        "seccion": "robo_ticket",
        "clase": 2,
        "usable": "cambios",
    },
    "ticket_rt_mayor_clase": {
        "seccion": "robo_ticket",
        "clase": 0,
        "usable": "cambios",
    },
}

PROBABILIDAD_TICKET = {
    2: 0.50,
    3: 0.60,
    4: 0.75,
    5: 0.90,
}

PROBABILIDAD_TICKET_CLASE = {
    2: {0: 0.00, 1: 0.05, 2: 0.15, 3: 0.80},
    3: {0: 0.00, 1: 0.10, 2: 0.25, 3: 0.65},
    4: {0: 0.00, 1: 0.15, 2: 0.35, 3: 0.50},
    5: {0: 0.00, 1: 0.20, 2: 0.45, 3: 0.35},
}

PROBABILIDAD_TICKET_CLASE_ULTIMO = {
    0: 0.05,
    1: 0.25,
    2: 0.50,
    3: 0.20,
}