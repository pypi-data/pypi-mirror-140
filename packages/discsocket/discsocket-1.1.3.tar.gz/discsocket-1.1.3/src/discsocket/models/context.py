from ..httpClient import HTTPClient
from .components import ActionRow
from .user import User
from .message import Message
from .. import utils
from ..embed import Embed

class BaseContext:
    def __init__(self, http_client: HTTPClient, data):
        self.__http = http_client
        self.raw = data
        self.resolved = data['data'].get('resolved', None)
        try:
            for option in data['data']['options']:
                setattr(self, option['name'], option['value'])
        except KeyError:
            pass
        self.command = self.raw['data'].get('name', None)
        self.command_id = self.raw['data'].get('id', None)
        self.channel_id = self.raw.get('channel_id', None)
        self.id = self.raw.get('id', None)
        self.token = self.raw.get('token', None)
        self.type = self.raw.get('type', None)
        self.invoked_by = User(self.raw['member']['user'])
        self.callback_url = self.__http.build_url(f'interactions/{self.id}/{self.token}/callback')

    async def callback(self, content: str = '', embeds: list[Embed] = [], embed: Embed = None, components: list[ActionRow] = [], ephemeral: bool = False, _type: int = utils.CHANNEL_WITH_SOURCE):
        if len(embeds) > 0 and embed is not None:
            _embeds = embeds.insert(0, embed)
        
        elif embed is not None and len(embeds) == 0:
            _embeds = [embed]

        else:
            _embeds = embeds

        response_json = {
            "type": _type,
            "data": {
                "content": content,
                "embeds": [emb.build() for emb in _embeds if isinstance(emb, Embed)],
                "components": [ar.base for ar in components]
            }
        }

        if ephemeral:
            response_json['data']['flags'] = 64

        await self.__http.make_request('POST', f"interactions/{self.id}/{self.token}/callback", response_json)
        self.message = Message(self.__http, await self.__http.make_request('GET', f"webhooks/{self.raw['application_id']}/{self.token}/messages/@original"))

class SelectMenuContext(BaseContext):
    def __init__(self, http_client, data):
        super().__init__(http_client, data)
        self.unique_id = self.raw['data']['custom_id']
        self.values = self.raw['data']['values']
        self.used_by = User(self.raw['member']['user'])
        self.invoked_by = User(data['message']['interaction']['user'])

class ButtonContext(BaseContext):
    def __init__(self, http_client, data):
        super().__init__(http_client, data)
        self.unique_id = self.raw['data']['custom_id']
        self.invoked_by = User(self.raw['message']['interaction']['user'])
        self.used_by = User(self.raw['member']['user'])
