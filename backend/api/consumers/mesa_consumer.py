from channels.generic.websocket import AsyncWebsocketConsumer
import json


class MesaConsumer(AsyncWebsocketConsumer):

	async def connect(self):
		self.partida_id = self.scope["url_route"]["kwargs"]["partida_id"]
		self.room_group_name = f"mesa_{self.partida_id}"

		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name,
		)

		await self.accept()

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name,
		)

	async def mesa_updated(self, event):
		await self.send(text_data=json.dumps({
			"type": "mesa_updated",
			"partida_id": event["partida_id"],
		}))
