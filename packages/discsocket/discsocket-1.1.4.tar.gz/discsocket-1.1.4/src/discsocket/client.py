import inspect
from .socket import Socket
import importlib
from .decorators import Command, Event, Component

class Client(Socket):
    def __init__(self, gateway_version: int = 10):
        super().__init__(gateway_version=gateway_version)
        

    def load_extension(self, path_to_extension):
        """
    
            Loads an extension into the client
            ```
            import discsocket
            import pathlib

            client = discsocket.Client()
            for ext in [f"{f.parent}.{f.stem}" for f in pathlib.Path('extensions').glob('*.py')]:
                client.load_extension(ext)
            ```
        """

        extension = importlib.import_module(path_to_extension)
        setup = getattr(extension, 'setup')

        setup(self)

    def add_extension(self, extension):
        attrs = extension._insert()
        for attr in attrs:
            if isinstance(attr, Command):
                self._container.add_command(attr)
            elif isinstance(attr, Event):
                self._container.add_event(attr)

    def add_component(self, parent, unique_id, function, timeout: float = 0.0, is_single_use: bool = False):
        """
            Registers a component into the bot.
        """
    
        component = Component(parent, unique_id, function, timeout=timeout, is_single_use=is_single_use)
        self._container.add_component(component)

    def command(self, name, _type):
        
        """
        Decorator to add a command to listen for.
        ```
        import discsocket
        socket = discsocket.Socket()
        @socket.command('ping', discsocket.utils.SLASH)
        async def ping(ctx):
            await ctx.callback('pong')
        ```
        """
        
        def wrapper(function):
            if not inspect.iscoroutinefunction(function):
                raise TypeError("Command functions must be coroutine")

            self.unchecked_decorators['commands'].append(Command(name, function, _type))

        return wrapper


    def event(self, name):
        
        """
        Decorator to add an event to listen for.
        ```
        import discsocket
        socket = discsocket.Socket()
        @socket.event('ready')
        async def ready_listener():
            print(f"{socket.user.username} is online")
        ```
        """

        def wrapper(function):
            if not inspect.iscoroutinefunction(function):
                raise TypeError("Event functions must be corotuine")

            self.unchecked_decorators['events'].append(Event(name, function))
        return wrapper


    async def fetch_guild(self, guild_id: int):
        """
            Returns the data for a guild
        """

        data = await self._http.make_request('GET', f'guilds/{guild_id}')
        try:
            return data
        except Exception as e:
            raise e

    async def fetch_user(self, user_id: int):
        """
            Returns the data for a user
        """

        data = await self._http.make_request('GET', f'users/{user_id}')
        try:
            return data
        except Exception as e:
            raise e


