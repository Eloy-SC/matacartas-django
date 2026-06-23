from channels.generic.websocket import AsyncWebsocketConsumer
import json

class SalaEsperaConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.partida_id = self.scope["url_route"]["kwargs"]["partida_id"]

        self.room_group_name = f"partida_{self.partida_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def room_updated(self, event):
        await self.send(text_data=json.dumps({
            "type": "room_updated",
            "partida_id": event["partida_id"],
        }))
    
    async def partida_iniciada(self, event):
        await self.send(text_data=json.dumps({
            "type": "partida_iniciada"
        }))