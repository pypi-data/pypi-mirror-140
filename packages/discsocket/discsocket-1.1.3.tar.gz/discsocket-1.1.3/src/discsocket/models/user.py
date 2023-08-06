"""
Discord User model
"""

from .. import utils

class User:
    """Represents a Discord user"""

    def __init__(self, data):
        self.raw = data
        self.id = int(data['id']) # Discord sends the ID as strings
        self.discriminator = int(data['discriminator']) # Sent as string
        self.name = data['username']

    @property
    def avatar_url(self):
        return utils.return_cdn_avatar(self.raw)
    
    @property
    def username(self):
        return self.name + '#' + str(self.discriminator)