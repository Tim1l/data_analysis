import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import json
from datetime import datetime, timedelta
import pytz

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return obj.decode('utf-8', 'ignore')
        return super(DateTimeEncoder, self).default(obj)

api_id = '' 
api_hash = ''
phone = '+'

async def main():
    async with TelegramClient('my_session.session', api_id, api_hash) as client:
        if not await client.is_user_authorized():
            client.send_code_request(phone)
            try:
                client.sign_in(phone, input('Enter the code: '))
            except SessionPasswordNeededError:
                client.sign_in(password=input('Password: '))
        
        chat_id = -823501060

        try:
            chat = await client.get_entity(chat_id)
        except Exception as e:
            print(f"Could not fetch chat: {e}")
            return

        chat_name = chat.title if hasattr(chat, 'title') else f"{chat.first_name} {chat.last_name}"
        print(f"Chat: {chat_name}")

        days = 10 #int(input("Enter the number of days: "))

        tz = pytz.UTC
        end_date_dt = datetime.now(tz)
        start_date_dt = end_date_dt - timedelta(days=days)

        messages = []
        async for message in client.iter_messages(chat, offset_date=end_date_dt):
            if message.date >= start_date_dt:
                messages.append(message)
            elif message.date < start_date_dt:
                break

        if not messages:
            print("No messages found in the chat.")
            return

        messages_list = []
        for message in messages:
            message_dict = message.to_dict()
            messages_list.append(message_dict)

        with open('chat_messages_list.json', 'w', encoding='utf-8') as f:
            json.dump(messages_list, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder)

        print(f"Retrieved {len(messages)} messages and saved them to chat_messages_list.json.")

# Call the main function using asyncio.run()
asyncio.run(main())
