from django.shortcuts import render, redirect
import random
import string
from .models import Room, Message
# Create your views here.
def home(request):
    session = request.session
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        if not session.get('name'):
            session['name'] = name
        return redirect('chat', code=code)
    return render(request, 'base/home.html', {'name': session['name'] if 'name' in session else None})


def chat(request, code):
    room = Room.objects.get(code=code)
    messages = Message.objects.filter(room=room).order_by('-created_at')
    return render(request, 'base/chat.html', {"room": room, "messages": messages})
    
def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def create_room(request):
    code = generate_random_string(6).upper()
    room = Room.objects.create(code=code)
    if room:
        return redirect('chat', code=room.code)
    else:
        return render(request, 'base/home.html', {'error': 'Failed to create room'})