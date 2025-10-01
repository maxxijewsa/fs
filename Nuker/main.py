try:
    import os
    import sys
    import time
    import json
    import utils
    import ctypes
    import base64
    import keyboard
    import pyperclip
    import subprocess
    from datetime import datetime
except ImportError as e:
    print(e)
    import os
    print("Installing modules")
    os.system('pip uninstall httpx')
    os.system('pip install requests pyperclip colorama keyboard httpx[http2]')
    print("Installed all modules; you can now restart this script")
    input("Press enter to exit")
    exit()

version = 1729
os.makedirs('db', exist_ok=True)

class Bot:
    def __init__(self):
        self.name = None
        self.token = None
        self.guild = None
        self.gname = None
        self.inv = None

    def Load(self):
        if os.path.exists("db/bots.json"):
            with open("db/bots.json", "r") as file:
                return json.load(file)
        return {}

    def Save(self, bots):
        if not os.path.exists("db/bots.json"):
            os.makedirs("db", exist_ok=True)
        with open("db/bots.json", "w") as file:
            json.dump(bots, file, indent=4)

    def SetToken(self, token, name, invite):
        self.token = token
        self.name = name
        self.inv = invite

    def SetGuild(self, guild, gname):
        self.guild = guild
        self.gname = gname

logger = utils.Logger(format="horizontal")
bot = Bot()

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    with open('config.json', 'w') as f:
        json.dump({
        "threads": 100,
        "proxyless": True,
        "whitelist": ["your id"],
        "og": False,
        "http2": False
    }, f, indent=4)
    with open('config.json', 'r') as f:
        config = json.load(f)

threads = config.get('threads', 50)
proxyless = config.get('proxyless', True)
whitelist = config.get('whitelist', [])
og = config.get('og', False)
http2 = config.get('http2', True)
if og:
    theme = utils.OG_Ascii()
else:
    theme = utils.Ascii()
theme.init()

def initBot():
    while True:
        theme.run()
        logger.inf("Enter 'list' to get all the bot tokens from database")
        try:
            token = pyperclip.paste().strip()
            if token and utils.Check(token).base64_check():
                clip = logger.inp(f"Use token ({token[:40]}...) from clipboard? [Y/N] ").strip().lower()
                if clip == 'y':
                    inst = utils.Check(token)
                    check, invite, id = inst.check()
                    if check == True:
                        bot.id = id
                        bots = bot.Load()
                        if token not in bots:
                            theme.run()
                            logger.inf("New token has been found. Saving it in database")
                            bot_alias = logger.inp("Enter bot alias (A name for the bot): ")
                            note = logger.inp("Enter note (A note for the bot, eg: very cool bot): ")
                            added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            bots[token] = {
                                "bot alias": bot_alias,
                                "added at": added_at,
                                "note": note,
                                "invite": invite
                            }
                            bot.Save(bots)
                            theme.run()
                            logger.dbg("Token added successfully.")
                        bot.SetToken(token, inst.get_name(), invite)
                        break
                    else:
                        theme.run()
                        logger.err("Token is incorrect")
                        time.sleep(1)
                        logger.inp("Press ENTER to retry")

        except Exception as e:
            logger.err(e)

        token = logger.inp("Token ")

        if token.lower() == "list":
            bots = bot.Load()
            if bots:
                theme.run()
                for bot_token, details in bots.items():
                    logger.inf(f"Token: {bot_token}", alias=details['bot alias'], note=details['note'])
                logger.inp("Press ENTER")
            else:
                logger.err("Nothing in db")
            continue

        try:
            inst = utils.Check(token)
            check, invite, id = inst.check()
            if check == True:
                bot.id = id
                bots = bot.Load()
                if token not in bots:
                    theme.run()
                    logger.inf("New token has been found. Saving it in database")
                    bot_alias = logger.inp("Enter bot alias (A name for the bot): ")
                    note = logger.inp("Enter note (A note for the bot, eg: very cool bot): ")
                    added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    bots[token] = {
                        "bot alias": bot_alias,
                        "added at": added_at,
                        "note": note,
                        "invite": invite
                    }
                    bot.Save(bots)
                    theme.run()
                    logger.dbg("Token added successfully.")
                bot.SetToken(token, inst.get_name(), invite)
                break
            else:
                theme.run()
                logger.err("Token is incorrect")
                time.sleep(1)
                logger.inp("Press ENTER to retry")

        except Exception as e:
            logger.ftl(e)


def initGuild():
    token = bot.token
    inst = utils.Check(token)
    while True:
        theme.run()
        logger.inf("Enter 'list' to get all guild ids")
        logger.inf(f"Bot's invite link", invite=bot.inv)
        try:
            guild_id = pyperclip.paste().strip()
            if int(guild_id) > 100000000000000:
                clip = logger.inp(f"Use guild ID ({guild_id[:10]}...) from clipboard? [Y/N] ").strip().lower()
                if clip == 'y':
                    inst = utils.Check(token)
                    chk, name = inst.guild(guild_id)
                    if chk == True:
                        logger.inf(f"Logged in", name=name)
                        bot.SetGuild(guild_id, name)
                        break
                    else:
                        theme.run()
                        logger.err("Guild ID is incorrect or failed to fetch")
                        time.sleep(1)
                        logger.inp("Press ENTER to retry")

        except Exception as e:
            pass
        try:
            guild_id = logger.inp("Guild ID: ")
            if guild_id.lower() == "list":
                guilds = inst.get_guilds()
                if guilds and isinstance(guilds, list):
                    theme.run()
                    for guild in guilds:
                        logger.inf(f"Guild ID: {guild['id']}", name=guild['name'])
                    logger.inp("Press ENTER")
                else:
                    logger.err("Failed to fetch guilds or no guilds found")
                    logger.inp("Press ENTER")
                continue
            chk, name = inst.guild(guild_id)
            if chk == True and guild_id is not None:
                logger.inf(f"Logged in", guild=name)
                bot.SetGuild(guild_id, name)
                break
            else:
                theme.run()
                logger.err("Guild ID is incorrect or failed to fetch")
                time.sleep(1)
                logger.inp("Press ENTER to retry")

        except Exception as e:
            logger.ftl(e)

    logger.inp("Press ENTER")


def main():
    whitelist.append(str(bot.id))
    nuker = utils.Nuker(token=bot.token, guild=bot.guild, threads=threads, proxyless=proxyless, whitelist=whitelist, http2=http2)
    theme.bot_name = bot.name
    theme.guild_name = bot.gname
    _options = {
        "Create Channels": {
            "function": nuker.CreateChannel
        },
        "Delete Channels": {
            "function": nuker.DeleteAllChannels
        },
        "Lock Channels": {
            "function": nuker.LockAllChannels
        },
        "Unlock Channels": {
            "function": nuker.UnlockAllChannels
        },
        "Rename Channels": {
            "function": nuker.RenameAllChannels
        },
        "Shuffle Channels": {
            "function": nuker.ShuffleChannels
        },
        "Spam All Channels": {
            "function": nuker.Spam
        },
        "Webhook Spam Channels": {
            "function": nuker.SpamWH
        },
        "Create Roles": {
            "function": nuker.CreateRoles
        },
        "Delete Roles": {
            "function": nuker.DeleteAllRoles
        },
        "Grant Role": {
            "function": nuker.GrantRole
        },
        "Rename Roles": {
            "function": nuker.RenameAllRoles
        },
        "Grant Admin": {
            "function": nuker.Admin
        },
        "Grant Everyone Admin": {
            "function": nuker.EAdmin
        },
        "Mass Ban": {
            "function": nuker.MassBan
        },
        "Mass Kick": {
            "function": nuker.MassKick
        },
        "Prune Members": {
            "function": nuker.MassPrune
        },
        "Mass Nick": {
            "function": nuker.MassNick
        },
        "Mass DM": {
            "function": nuker.MassDM
        },
        "Delete Emojis": {
            "function": nuker.DeleteEmojis
        },
        "Create Emojis": {
            "function": nuker.CreateEmojis
        },
        "Change Server Name": {
            "function": nuker.RenameServer
        },
        "Leave Guild": {
            "function": nuker.LeaveGuild
        },
        "Leave All Guilds": {
            "function": nuker.LeaveAllGuilds
        },
        "Full Nuke": {
            "function": nuker.FullNuke
        },
        "Guild Info": {
            "function": nuker.ServerInfo
        },
        "Get Invite Link": {
            "function": nuker.GetInviteLink
        },
        "Unban User": {
            "function": nuker.UnbanUser
        },
        "Unban All Users": {
            "function": nuker.UnbanAll
        },
        "Scrape Servers": {
            "function": nuker.ScrapeGuilds
        },
        "Change Guild": {
            "function": nuker.ChangeGuild
        },
        "Change Theme": {
            "function": theme.ChangeTheme
        },
        "Credits": {
            "function": theme.run
        },
        "RPS Check": {
            "function": nuker.RPSCheck
        },
        "Exit": {
            "function": theme.run
        }
    }

    for option in _options:
        theme.options.append(option)

    options = {str(index + 1): name for index, name in enumerate(_options)}

    while True:
        ctypes.windll.kernel32.SetConsoleTitleW("Lithium | V5 | Menu                   [discord.gg/pop]")
        os.system('mode con: cols=200 lines=40')
        try:
            theme.run(False)
            try:
                index = logger.inp("Option")
                if index in options:
                    os.system('mode con: cols=150 lines=40')
                    theme.run()
                    name = options[index]
                    func = _options[name]["function"]
                    ctypes.windll.kernel32.SetConsoleTitleW(f"Lithium | V5 | {name}                   [discord.gg/pop]")
                    if name == "Create Channels":
                        name = logger.inp("Name")
                        if name == "":
                            continue
                        amount = logger.inp("Amount", integer=True)
                        if amount == 0:
                            continue
                        nuker.run(func, amount, name)
                    elif name == "Create Emojis":
                        name = logger.inp("Name")
                        if name == "":
                            continue
                        amount = logger.inp("Amount", integer=True)
                        if amount == 0:
                            continue
                        nuker.run(func, 1, amount, name)

                    elif name == "Create Roles":
                        name = logger.inp("Name")
                        if name == "":
                            continue
                        amount = logger.inp("Amount", integer=True)
                        if amount == 0:
                            continue
                        nuker.run(func, 1, name, amount)
                    
                    elif name == "Rename Channels" or name == "Rename Roles" or name == "Mass Nick":
                        name = logger.inp("New name")
                        if name == "":
                            continue
                        nuker.run(func, 1, name)

                    elif name == "Spam All Channels" or name == "Webhook Spam Channels":
                        message = logger.inp("Message")
                        if message == "":
                            continue
                        amount = logger.inp("Amount", integer=True)
                        if amount > 0:
                            nuker.run(func, 1, message, amount)



                    elif name == "Grant Role":
                        role = logger.inp("Role (ID)", integer=True)
                        user = logger.inp("User (ID)", integer=True)
                        if role > 1000000000000000 and user > 1000000000000000:
                            nuker.run(func, 1, user, role)

                    elif name == "Unban User" or name == "Grant Admin":
                        user = logger.inp("User (ID)", integer=True)
                        if user > 1000000000000000:
                            nuker.run(func, 1, user)

                    elif name == "Mass Ban":
                        ids = logger.inp("Ban IDS? (Enter Y to ban ids from db/ids.txt ; Press ENTER to ban server users)")
                        if ids.lower() == "y":
                            utils.IDS().run()
                            nuker.run(func, 1, True)
                        else:
                            nuker.run(func, 1)

                    elif name == "Mass Kick":
                        ids = logger.inp("Kick IDS? (Enter Y to ban ids from db/ids.txt ; Press ENTER to kick server users)")
                        if ids.lower() == "y":
                            utils.IDS().run()
                            nuker.run(func, 1, True)
                        else:
                            nuker.run(func, 1)

                    elif name == "Change Server Name":
                        name = logger.inp("New name")
                        if name != "":
                            nuker.run(func, 1, name)

                    elif name == "Mass DM":
                        msg = logger.inp("Message to send")
                        if msg != "":
                            nuker.run(func, 1, msg)

                    elif name == "Leave Guild" or name == "Leave All Guilds":
                        sure = logger.inp("Are you sure? (Enter Y if you are)")
                        if sure.lower() == "y":
                            sure2 = logger.inp("Are you 1000% sure? (Enter Y if you are)")
                            if sure2.lower() == "y":
                                nuker.run(func, 1)
                                initGuild()
                        else:
                            continue

                    elif name == "Full Nuke":
                        name = logger.inp("Channel Name")
                        if name == "":
                            continue
                        amount = logger.inp("Channel Amount", integer=True)
                        if amount == 0:
                            continue
                        message = logger.inp("Message")
                        amt = logger.inp("Spam Amount", integer=True)
                        nuker.run(_options["Delete Channels"]["function"], 1)
                        nuker.run(_options["Create Channels"]["function"], amount, name)

                        if amt != 0:
                            nuker.run(_options["Spam All Channels"]["function"], 1, message, amt)

                    elif name == "Credits":
                        theme.run()
                        logger.dbg("Made by @neonic69420 || discord.gg/pop :)")

                    elif name == "Exit":
                        sure = logger.inp("Are you sure? (Enter Y if you are)")
                        if sure.lower() == "y":
                            exit()

                    elif name == "Change Guild":
                        sure = logger.inp("Are you sure? (Enter Y if you are)")
                        if sure.lower() != "y":
                            continue
                        theme.options = []
                        initGuild()
                        main()

                    else:
                        nuker.run(func, 1)

                    logger.inp("Press ENTER")
                else:
                    theme.run()
                    logger.err("Invalid option")
                    logger.inp("Press enter to continue")
            except ValueError:
                theme.run()
                logger.err("Option must be an integer")
                logger.inp("Press enter to continue")
        except Exception as e:
            logger.err("An error occurred", error=e)
            logger.inf("Please report it at discord.gg/pop (Tools server @ errors channel)")
            logger.inp("Press enter to continue")


if utils.__version_override__ != version - 2:
    __name__ = utils.__version_override__

if __name__ == "__main__":
    ctypes.windll.kernel32.SetConsoleTitleW("Lithium | V5 | Authenticating                   [discord.gg/pop]")
    os.system('mode con: cols=150 lines=40')
    initBot()
    initGuild()
    main()
