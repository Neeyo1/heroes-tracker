import json
from datetime import datetime, timezone

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import MapGroup, Map, Hero
from django.core.serializers import serialize
from asgiref.sync import sync_to_async
from django.forms.models import model_to_dict
from rest_framework.renderers import JSONRenderer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.clan_name = self.scope["url_route"]["kwargs"]["clan_name"]
        self.room_group_name = f"chat_{self.clan_name}"
        self.user = self.scope["user"]
        print(self.user)

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json["action"]
        if action == "get_data":
            #await self.channel_layer.group_send(
            #    self.room_group_name, {"type": "chat.get.data", "message": "get some data from db"}
            #)
            await self.chat_get_data(self)
        elif action == "set_data":
            map = text_data_json["map"]
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.set.data", "map": map}
            )
        elif action == "get_user":
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.get.user"}
            )
        #else:
        #    await self.channel_layer.group_send(
        #        self.room_group_name, {"type": "chat.message", "message": action}
        #    )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def chat_get_data(self, event):
        
        all_data, all_maps = await sync_to_async(self.get_data_from_db)()

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"action": "all_data", "message": all_data}))
        await self.send(text_data=json.dumps({"action": "all_maps", "message": all_maps}))

    async def chat_set_data(self, event):
        map_updated = await sync_to_async(self.set_data_to_db)(event["map"])

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"action": "single_data", "message": map_updated}))

    async def chat_get_user(self, event):
        message = self.user.username

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"action": "user", "message": message}))

    def get_data_from_db(self):
        #print(Hero.objects.all().__dict__)
        data_dict = {}
        hero_index = 0
        heroes = Hero.objects.all()
        date_now = datetime.now(timezone.utc)
        maps_all = []   #for client side to track only specific maps
        for hero in heroes:
            data_dict[hero_index] = {"name": hero.name, "lvl": hero.lvl, "maps": {}}
            maps = hero.maps.all()
            map_list = {}
            for map in maps:
                if map.map_group.name not in map_list:
                    map_list[map.map_group.name] = {0: {'name': map.name, 'updated_by': map.updated_by.username, 'updated_at': int((date_now - map.updated_at).total_seconds())}}
                else:
                    map_index = len(map_list[map.map_group.name])
                    map_list[map.map_group.name][map_index] = {'name': map.name, 'updated_by': map.updated_by.username, 'updated_at': int((date_now - map.updated_at).total_seconds())}
                maps_all.append(map.name)    #for client side to track only specific maps
            data_dict[hero_index]['maps']= map_list
            hero_index += 1
        return data_dict, maps_all
    
    def set_data_to_db(self, map_name):
        date_now = datetime.now(timezone.utc)
        map = Map.objects.get(name = map_name)
        map.updated_by = self.user
        map.save()
        return str({'name': map.name, 'updated_by': map.updated_by.username, 'updated_at': int((date_now - map.updated_at).total_seconds())})