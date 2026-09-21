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

def notificar_inicio_partida(partida_id):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"partida_{partida_id}",
        {
            "type": "partida_iniciada"
        }
    )

def notificar_mesa_actualizada(partida_id):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"mesa_{partida_id}",
        {
            "type": "mesa_updated",
            "partida_id": partida_id
        }
    )

def notificar_mano_finalizada(partida_id, mano_id):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"mesa_{partida_id}",
        {
            "type": "mano_finalizada",
            "partida_id": partida_id,
            "mano_id": mano_id,
        }
    )

'''
def comprobar_claves(obj, ruta="datos_final_partida"):
    if isinstance(obj, dict):
        for clave, valor in obj.items():
            if not isinstance(clave, str):
                print(
                    f"CLAVE PROBLEMÁTICA: {ruta}[{clave!r}] "
                    f"({type(clave).__name__})"
                )

            comprobar_claves(valor, f"{ruta}[{clave!r}]")

    elif isinstance(obj, (list, tuple)):
        for i, valor in enumerate(obj):
            comprobar_claves(valor, f"{ruta}[{i}]")
'''

def notificar_finalizacion_partida(partida_id, datos_final_partida):
    channel_layer = get_channel_layer()

    '''
    print("================================================================================")
    print("DATOS FINAL PARTIDA:")
    print(datos_final_partida)
    print(type(datos_final_partida))
    print("================================================================================")
    print("COMPROBACION DE CLAVES:")
    comprobar_claves(datos_final_partida)
    print("================================================================================")
    '''
    async_to_sync(channel_layer.group_send)(
        f"mesa_{partida_id}",
        {
            "type": "partida_finalizada",
            "partida_id": partida_id,
            "datos_final_partida": datos_final_partida,
        }
    )