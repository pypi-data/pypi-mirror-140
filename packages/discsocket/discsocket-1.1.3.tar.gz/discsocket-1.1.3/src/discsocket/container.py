from . import utils

class Container:
    def __init__(self):
        self.commands = {}
        self.components = {}
        self.events = {}
        self.user_commands = {}
        self.message_commands = {}


    def add_command(self, command):
        match command.type:
            case utils.SLASH:
                self.commands[command.name] = command
            case utils.MESSAGE:
                self.message_commands[command.name] = command
            case utils.USER:
                self.user_commands[command.name] = command

    def add_event(self, event):
        try:
            self.events[event.name].append(event)
        except KeyError:
            self.events[event.name] = [event]

    def add_component(self, component):
        self.components[component.custom_id] = component