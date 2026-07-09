from django.urls import re_path
from .consumers.mesa_consumer import MesaConsumer
from .consumers.sala_espera_consumer import SalaEsperaConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/partidas/(?P<partida_id>\d+)/$",
        SalaEsperaConsumer.as_asgi(),
    ),
    re_path(
        r"ws/partidas/(?P<partida_id>\d+)/mesa/$",
        MesaConsumer.as_asgi(),
    ),
]