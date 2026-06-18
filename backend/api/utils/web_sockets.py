from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notificar_sala_actualizada(partida_id):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"partida_{partida_id}",
        {
            "type": "room_updated",
            "partida_id": partida_id
        }
    )