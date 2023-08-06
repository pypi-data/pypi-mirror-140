from enum import Enum

class Avatars(Enum):
    """
    Enum for the avatars.
    """
    blurple = 0
    grey = 1
    gray = 1
    green = 2
    orange = 3
    red = 4

    def __str__(self):
        return self.name

def return_cdn_avatar(data):
    if data['avatar'] is not None:
        animated = data['avatar'].startswith('a_')
        suffix = 'gif' if animated else 'png'
        return f'https://cdn.discordapp.com/avatars/{data["id"]}/{data["avatar"]}.{suffix}?size=1024'
    else:
        return f"https://cdn.discordapp.com/embed/avatars/{int(data['id']) % len(Avatars)}.png"
