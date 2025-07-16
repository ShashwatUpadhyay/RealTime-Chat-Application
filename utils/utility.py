import string
import random
from base.models import Room


def generate_random_string(length):
    while True:
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(length))
        if not Room.objects.filter(code=random_string).exists():
            return random_string
