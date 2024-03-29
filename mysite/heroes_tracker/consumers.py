import json
from datetime import datetime, timezone
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import MapGroup, Map, Hero, Clan
from django.contrib.auth.models import User
from django.core.serializers import serialize
from asgiref.sync import sync_to_async
from django.forms.models import model_to_dict
from rest_framework.renderers import JSONRenderer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.clan_name = self.scope["url_route"]["kwargs"]["clan_name"]
        self.room_group_name = f"chat_{self.clan_name}"
        
        self.user = self.scope["user"]
        print(str(self.user))

        if str(self.user) == "AnonymousUser":
            is_user_validated = await sync_to_async(self.validate_user)()
            if not is_user_validated:
                return

        clan = await sync_to_async(self.get_all_clans)()
        if clan == None:
            return
        
        access_to_clan = await sync_to_async(self.check_access_to_clan)(clan)
        if not access_to_clan:
            return

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
            map_updated = await sync_to_async(self.set_data_to_db)(map)
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.set.data", "map": map_updated}
            )
        elif action == "get_user":
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.get.user"}
            )
        elif action == "set_user":
            user = text_data_json["user"]
            self.user = user
            await self.send(text_data=json.dumps({"message": "OK"}))
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
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"action": "single_data", "message": event['map']}))

    async def chat_get_user(self, event):
        message = self.user

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
                    map_list[map.map_group.name] = {0: {'name': map.name, 'updated_by': map.updated_by, 'updated_at': int((date_now - map.updated_at).total_seconds())}}
                else:
                    map_index = len(map_list[map.map_group.name])
                    map_list[map.map_group.name][map_index] = {'name': map.name, 'updated_by': map.updated_by, 'updated_at': int((date_now - map.updated_at).total_seconds())}
                maps_all.append(map.name)    #for client side to track only specific maps
            data_dict[hero_index]['maps']= map_list
            hero_index += 1
        return data_dict, maps_all
    
    def set_data_to_db(self, map_name):
        date_now = datetime.now(timezone.utc)
        try:
            map = Map.objects.get(name = map_name)
            map.updated_by = self.user
            map.save()
            return {'name': map.name, 'updated_by': map.updated_by, 'updated_at': int((date_now - map.updated_at).total_seconds())}
        except:
            pass

    def get_all_clans(self):
        print(self.clan_name)
        try:
            clan = Clan.objects.get(name = self.clan_name)
        except Clan.DoesNotExist:
            clan = None
        print(clan)
        return clan
    
    def check_access_to_clan(self, clan):
        members = clan.members.all()
        if self.user in members:
            return True
        else:
            return False
        
    def validate_user(self):
        url_params = parse_qs(self.scope['query_string'].decode('utf8'))
        print(url_params)
        try:
            user = User.objects.get(username=url_params['login'][0])
            print("User OK")
        except Exception as e:
            print(e)
            return False
        if not user.check_password(url_params['password'][0]):
            return False
        else:
            self.user = user
            print("Password OK")
            return True