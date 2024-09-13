import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer


class AsyncMailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("email_notifications", self.channel_name)
        await self.accept()

        # await self.send(json.dumps({
        #     'message': 'connected'
        # }))


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("email_notifications", self.channel_name)


    async def new_email(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

