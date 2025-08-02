import google.generativeai as genai
from .models import Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from rtcom.settings import GEMINI_API_KEY,SYSTEM_CONTEXT
from background_task import background
import time
# Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# Load Gemini model
model = genai.GenerativeModel("gemini-2.5-pro")
models = genai.list_models()


def build_chat_history(room_id):
    messages = Message.objects.filter(room__id=room_id,content__icontains = '@bot').order_by("created_at")  # Or your ordering field

    history=[]
    for msg in messages:
        role = "user" if msg.user != "BOT" else "model"  
        history.append({
            "role": role,
            "parts": [msg.content]
        })
        
    history.insert(0, {
        "role": "user",
        "parts": [SYSTEM_CONTEXT]
    })

    return history

@background(schedule=1)
def ask_gemini(roomid, roomcode ,prompt):
    async_to_sync(channel_layer.group_send)(
            f"chat_{roomcode}",
            {
                "type": "generating",
                "value": json.dumps({"user":"BOT","content":"Generating..."}),
            }
        )
    try:
        print("Running ask_gemini")
        history = build_chat_history(roomid)

        chat = model.start_chat(history=history)
        print("Context taken, Generating response...")
        response = chat.send_message(prompt)
        print("Response generated")
        Message.create_message(roomid, "BOT", response.text)
        channel_layer = get_channel_layer()
        data = {
            "user" : "BOT",
            "content" : response.text,
            "created_at" : ''
        }
        async_to_sync(channel_layer.group_send)(
            f"chat_{roomcode}",
            {
                "type": "send_sdp",
                "value": json.dumps(data),
            }
        )
        print("Response sent")
        return response.text
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    
@background(schedule=1)
def dummy_task(num):
    print("Running dummy task")
    time.sleep(5)
    print("dummy task done")