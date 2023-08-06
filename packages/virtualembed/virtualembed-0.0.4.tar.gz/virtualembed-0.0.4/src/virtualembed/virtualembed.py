import json
import base64

from .embedimage import EmbedImage
import urllib.request


class VirtualEmbed:
    def __init__(self, title: str = "", description: str = "", color: str = "", bot_name:str="Clyde", bot_avatar:str=""):
        self.title = title
        self.description = description
        self.color = color
        self.bot_name = bot_name
        self.bot_avatar = bot_avatar
        self.json = {}
        self.json.setdefault("embed", {"fields": []})

    def get_embed_json(self):
        self.json["embed"]["title"] = self.title
        self.json["embed"]["description"] = self.description
        self.json["embed"]["color"] = self.color
        return self.json

    def get_base_url(self):
        return f"https://glitchii.github.io/embedbuilder/?username={self.bot_name}&verified=&avatar={self.bot_avatar}&data="

    def get_embed_as_image(self):
        html_encoded = urllib.parse.quote(str(json.dumps(self.get_embed_json())))
        message_bytes = html_encoded.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        embed_url = urllib.parse.quote(self.get_base_url() + base64_bytes.decode("utf-8"))
        screenshot = f"https://api.screenshotmachine.com?key=09b279&url={embed_url}&device=desktop&dimension=1024x768&format=jpg&selector=body%20%3E%20div%20%3E%20section.side2%20%3E%20div.msgEmbed"
        return EmbedImage(screenshot)

    def add_field(self, name: str, value: str, inline: bool):
        field = {
            "name": name,
            "value": value,
            "inline": inline
        }
        self.get_embed_json()["embed"]["fields"].append(field)

    def set_thumbnail(self, image_url: str):
        thumbnail = {
            "thumbnail": {                "url": image_url
            }
        }
        self.get_embed_json()["embed"].update(thumbnail)

    def set_image(self, image_url: str):
        thumbnail = {
            "image": {
                "url": image_url
            }
        }
        self.get_embed_json()["embed"].update(thumbnail)

    def set_author(self, name: str, icon_url: str = None):
        author = {
            "author": {
                "name": name,
                "icon_url": icon_url
            }
        }
        self.get_embed_json()["embed"].update(author)