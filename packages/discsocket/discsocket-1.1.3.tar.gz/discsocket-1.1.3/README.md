# discsocket

Python framework for Discord interactions.

# Installation
`pip install discsocket`

# Introduction
This is the code needed for a minimal application with an on_ready event
```py
import discsocket

socket = discsocket.Socket()

# Event names go in the event decorator
# The function can be named whatever
@socket.event('ready')
async def ready():
  print(f"{socket.user.username} is connected")
 
socket.run('token')
```

or if you want to make the bot function as a class
```py
import discsocket

class Socket(discsocket.Socket):
    def __init__(self):
        super().__init__(gateway_version=8)

    # Events in a class structure won't require a decorator
    # and instead follow the 'on_' + gateway_event format

    async def on_ready(self):
        print(f"{self.user.username} is online")

if __name__ == '__main__':
    Socket().run('token')
```
# Extensions
Extensions work to separate your code into different files so it is not all in a single file 

```py
import discsocket
from discsocket import ext

class Boop(ext.Extension):
    def __init__(self, socket):
        self.socket = socket

    # Example of a command within an extension
    @ext.Extension.command('boop', discsocket.utils.SLASH)
    async def boop(self, context: discsocket.models.BaseContext):
        await context.callback(content='boop!')

    # Example of a listener within an extension
    @ext.Extension.listener('message_create')
    async def message(self, message):
        print(message['content'])

def init_ext(socket):
    socket.add_ext(Boop(socket))
```

As an example, the above extension is in a folder called 'extensions'

```py

import discsocket
import pathlib

class Socket(discsocket.Socket):
    def __init__(self):
        super().__init__(gateway_version=8)
        self.load()

    def load(self):
        for ext in [f'{p.parent}.{p.stem}' for p in pathlib.Path('extensions').glob('*.py')]:
            try:
                self.add_extension(ext)
            except Exception as e:
                print(f"Failed to load {ext}.\n-> {e}")
            else:
                print(f"Loaded {ext}")

    async def on_ready(self):
        print(f"{self.user.username} is online")

if __name__ == '__main__':
    Socket().run('token')
```
    