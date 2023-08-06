from ..embed import Embed
from .message import Message
from .components import ActionRow
from ..httpClient import HTTPClient

class GuildTextChannel:
    def __init__(self, socket_client: HTTPClient, raw_data):
        self.__http = socket_client
        self.raw = raw_data
        self.id = self.raw['id']

    async def fetch_message(self, message_id):
        """Returns a message from the channel with the corresponding message id"""
        
        message = await self.__http.make_request('GET', f'channels/{self.id}/messages/{message_id}')
        return Message(self.__http, message)

    async def send(self, content: str = '', embeds: list[Embed] = [], embed: Embed = None, components: list[ActionRow] = []) -> Message:
        """Sends a message to this text channel. Returns a `Message` object."""
        if embed is not None:
            _embeds = embeds.insert(0, embed)
        else:
            _embeds = embeds

        message_json = {
            "content": content,
            "embeds": [emb.build() for emb in _embeds if isinstance(emb, Embed)]
        }

        if len(components) > 0:
            _components = [action_row.base for action_row in components if isinstance(action_row, ActionRow)]
            message_json['components'] = _components

        return Message(self.__http, await self.__http.make_request('POST', f'channels/{self.id}/messages', message_json))
