from dataclasses import dataclass

@dataclass
class ContrincanteDTO:
    contrincante_id: int
    nombre: str
    imagen: str
    color: str
    puntos: int
    cartas_cant: int
    carta_comodin: bool
    ticket: bool

@dataclass
class JugadorDTO:
    jugador_id: int
    nombre: str
    imagen: str
    color: str
    puntos: int
    cartas: list[str] | None
    carta_comodin: str | None
    acumulador_kills: int
    acumulador_deaths: int
    retirado: bool
    ticket: str | None
    ticket_usable: str | None

@dataclass
class RondaDTO:
    ronda_id: int
    ronda_num: int
    cartas: dict[str, str | None]
    cambios: int

@dataclass
class ManoDTO:
    mano_id: int
    mano_num: int
    ganador: str | None

@dataclass
class PartidaDTO:
    partida_id: int
    baraja_cant: int
    longitud: int
    disposicion_jugadores: list[str]
    turno_actual: str | None
    tiempo_max_turno: int
    partida_finalizada: bool

@dataclass
class MesaDTO:
    partida: PartidaDTO
    mano: ManoDTO
    rondas: list[RondaDTO]
    jugador: JugadorDTO
    contrincantes: list[ContrincanteDTO]

@dataclass
class ResumenRondaDTO:
    victoria: tuple[str, str] | None
    muerte: tuple[str, str] | None
    retiradas: list[str] | None
    efectos_inmediatos: list[tuple[str, str]] | None
    tickets_usados: list[tuple[str, str]] | None

@dataclass
class ResumenManoDTO:
    mano_num: int
    ronda_prep: ResumenRondaDTO
    ronda_1: ResumenRondaDTO
    ronda_2: ResumenRondaDTO
    ronda_3: ResumenRondaDTO
    ronda_com: ResumenRondaDTO
    efectos_extra_fin_mano: list[tuple[str, str]]
    ganador: str | None
