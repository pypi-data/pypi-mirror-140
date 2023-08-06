class ActionRow:
    def __init__(self, components: list):
        self.base = {"type": 1, "components": [component.base for component in components]}

class SelectMenuOption:
    def __init__(self, label: str, value, description: str ='', emoji: dict = {}):
        self.base = {"label": label, "description": description, "value": value, "emoji":emoji}

class SelectMenu:
    def __init__(self, custom_id, options):
        self.base = {"type": 3, "custom_id": custom_id, "options": [opt.base for opt in options if isinstance(opt, SelectMenuOption)]}

class ButtonStyle:
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5

class Button:
    def __init__(self, custom_id, style: int = ButtonStyle.PRIMARY, label: str = '', url: str = None, emoji: dict = None, disabled: bool = False):
        self.base = {"type": 2, "style": style, "label": label, "custom_id": custom_id, "disabled": disabled}
        if emoji is not None:
            self.base['emoji'] = emoji
        if style == ButtonStyle.LINK and url is not None:
            self.base['url'] = url

