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

@dataclass
class JugadorDTO:
    jugador_id: int
    nombre: str
    imagen: str
    color: str
    puntos: int
    cartas: list[str] | None
    carta_comodin: str | None

@dataclass
class RondaDTO:
    ronda_id: int
    ronda_num: int
    cartas: list[str] | None

@dataclass
class ManoDTO:
    mano_id: int
    mano_num: int

@dataclass
class PartidaDTO:
    partida_id: int
    baraja_cant: int
    disposicion_jugadores: list[str]
    turno_actual: str | None
    tiempo_max_turno: int

@dataclass
class MesaDTO:
    partida: PartidaDTO
    mano: ManoDTO
    rondas: list[RondaDTO]
    jugador: JugadorDTO
    contrincantes: list[ContrincanteDTO]
