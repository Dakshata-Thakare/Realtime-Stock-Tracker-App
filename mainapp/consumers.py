# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async, async_to_sync

class StockConsumer(AsyncWebsocketConsumer):
    def addToCeleryBeat(self,stockpicker):
        from django_celery_beat.models import PeriodicTask,IntervalSchedule   #from global to function based doing not knwo why
        task = PeriodicTask.objects.filter(name="every-10-seconds")
        # if len(task)>0:
        if task.exists(): #suggested
            task = task.first()
            args = json.loads(task.args)
            args = args[0]
            for x in stockpicker:
                if x not in args:
                    args.append(x)
            task.args = json.dumps([args])
            task.save()
        else:
            schedule,created = IntervalSchedule.objects.get_or_create(every=10,period=IntervalSchedule.SECONDS)
            task = PeriodicTask.objects.create(interval = schedule,name='every-10-seconds',task="mainapp.tasks.update_stock",args= json.dumps([stockpicker]))

    async def connect(self):
        print("🔥 CONNECT METHOD CALLED")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'stock_{self.room_name}' #'stock_%s' % self.room_name #Create Group Name
    
        await self.channel_layer.group_add( #Add User To Group
            self.room_group_name,
            self.channel_name
        )

        # Parse query_string
        query_params = parse_qs(self.scope["query_string"].decode())
        print("query_params: ",query_params)
        stockpicker = query_params['stockpicker']

        #add to celery beat
        # await self.addToCeleryBeat(stockpicker)
        await sync_to_async(self.addToCeleryBeat)(stockpicker) #suggested
        await self.accept()
        print(" WebSocket Connected.................")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("❌ WebSocket Disconnected.......")


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_stock_update',
                'message': message
            }
        )

    async def send_stock_update(self,event):
        message = event['message']
        print("type of message: ",type(message))
        print("message is : ",message)
        # await self.send(text_data=json.dumps({message}))
        await self.send(text_data=json.dumps({'message': message}))
