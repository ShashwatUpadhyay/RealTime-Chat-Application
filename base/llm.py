import google.generativeai as genai
from .models import Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from rtcom.settings import GEMINI_API_KEY,SYSTEM_CONTEXT
# Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")
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

def ask_gemini(roomid, roomcode ,prompt):
    history = build_chat_history(roomid)

    chat = model.start_chat(history=history)
    print("Context taken, Generating response...")
    response = chat.send_message(prompt)

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
    return response.text
