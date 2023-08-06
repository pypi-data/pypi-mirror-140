from __future__ import annotations
from typing import TypeVar

E = TypeVar('E', bound="Embed")

class Embed:
    def __init__(self, title: str = None, description: str = None, color = None):
        self.title = None if title is None else title
        self.description = None if description is None else description
        self.color = 0x2f3136 if color is None else color
        self.__built = {"type": "rich", "title": self.title, "description": self.description, "color": self.color}

    def add_field(self, name: str = None, value: str = None, inline: bool = False) -> E:
        """Adds a field object to the Embed"""
        if name is None:
            raise ValueError("Embed.field name expected string, received NoneType.")
        if value is None:
            raise ValueError("Embed.field value expected string, received NoneType.")
        if name is None and value is None:
            raise ValueError("Embed.field object cannot be empty.")

        try:
            self.__built['fields'].append({"name": name, "value": value, "inline": inline})
        except KeyError:
            self.__built['fields'] = [{"name": name, "value": value, "inline": inline}]

        return self

    def set_footer(self, text: str = None, icon_url: str = None) -> E:
        if text is None and icon_url is None:
            raise ValueError("Embed.footer object cannot be empty.")

        try:
            self.__built['footer']['text'] = text
            if icon_url is not None:
                self.__built['footer']['icon_url'] = icon_url
        except KeyError:
            self.__built['footer'] = {"text": text}
            if icon_url is not None:
                self.__built['footer']['icon_url'] = icon_url

        return self

    def set_author(self, name: str = None, url: str = None, icon_url: str = None) -> E:
        if name is None and url is None and icon_url is None:
            raise ValueError("Embed.author object cannot be empty.")

        try:
            if name is not None:
                self.__built['author']['name'] = name
            if url is not None:
                self.__built['author']['url'] = url
            if icon_url is not None:
                self.__built['author']['icon_url'] = icon_url
        except KeyError:
            self.__built['author'] = {}
            if name is not None:
                self.__built['author']['name'] = name
            if url is not None:
                self.__built['author']['url'] = url
            if icon_url is not None:
                self.__built['author']['icon_url'] = icon_url

        return self

    def set_image(self, image_url: str):
        self.__built['image'] = {}
        self.__built['image']['url'] = image_url

        return self

    def set_thumbnail(self, thumbnail_url: str):
        self.__built['thumbnail'] = {}
        self.__built['thumbnail']['url'] = thumbnail_url

    def build(self) -> dict:
        return self.__built