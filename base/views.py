from django.shortcuts import render, redirect
import random
import string
from .models import Room, Message
from utils.utility import generate_random_string
from faker import Faker
fake = Faker()
# Create your views here.
def home(request):
    session = request.session
    if not session.get('name'):
        session['name'] = fake.name()
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        if not session.get('name'):
            session['name'] = name
        return redirect('chat', code=code)
    return render(request, 'base/home.html', {'name': session['name'] if 'name' in session else fake.name()})


def chat(request, code):
    try:
        room = Room.objects.get(code=code)
        messages = Message.objects.filter(room=room)
        return render(request, 'base/chatrt.html', {"room": room, "messages": messages})
    except Room.DoesNotExist:
        return redirect('home')

def create_room(request):
    code = generate_random_string(6).upper()
    room = Room.objects.create(code=code)
    if room:
        return redirect('chat', code=room.code)
    else:
        return render(request, 'base/home.html', {'error': 'Failed to create room'})