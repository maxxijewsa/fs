import os
import re
import json
import utils
import colorama

logger = utils.Logger(format="horizontal")

class Ascii:
    def __init__(self):
        
        self.version = "5.3"
        colorama.init(autoreset=True)
        self.bot_name = "Null"
        self.guild_name = "Null"
        self.options = []
        self.theme = {}
        self.default = {
            "loaded": "dark",
            "blood": {
                "start": "231, 13, 13",
                "end": "34, 90, 68"
            },
            "cherry": {
                "start": "240, 197, 197",
                "end": "153, 94, 231"
            },
            "hulky triv": {
                "start": "198, 55, 190",
                "end": "34, 237, 80"
            },
            "fucking blue nigger": {
                "start": "23, 44, 83",
                "end": "80, 52, 244"
            },
            "fading green nigger": {
                "start": "38, 84, 101",
                "end": "47, 214, 92"
            },
            "dark": {
                "start": "76, 45, 128",
                "end": "153, 27, 14"
            },
            "elite": {
                "start": "205, 18, 198",
                "end": "223, 9, 1"
            },
            "hellfire": {
                "start": "124, 18, 128",
                "end": "215, 106, 1"
            },
            "light pink": {
                "start": "193, 226, 248",
                "end": "255, 105, 220"
            },
            "lush": {
                "start": "139, 108, 71",
                "end": "10, 131, 25"
            },
            "metalic": {
                "start": "80, 177, 211",
                "end": "243, 35, 53"
            },
            "nano": {
                    "start": "250, 8, 20",
                    "end": "12, 146, 129"
            },
            "orange": {
                    "start": "173, 8, 15",
                    "end": "190, 174, 51"
            },
            "pink": {
                "start": "220, 105, 237",
                "end": "124, 239, 230"
            }
        }

    def init(self):
        try:
            if os.path.exists('db/themes.json'):
                with open('db/themes.json', 'r') as f:
                    themes = json.load(f)
                    loaded = themes["loaded"]
                    self.theme = themes[loaded]
            else:
                with open("db/themes.json", 'w') as f:
                    f.write(json.dumps(self.default, indent=4))
                self.init()
        except:
            with open("db/themes.json", 'w') as f:
                f.write(json.dumps(self.default, indent=4))
                self.init()


    @staticmethod
    def gradient(start, end, steps):
        if not all(isinstance(i, int) for i in start) or not all(isinstance(i, int) for i in end):
            raise ValueError("Start and end values must be lists of integers.")
        step = [(end[i] - start[i]) / steps for i in range(3)]
        grad = [
            tuple(int(start[i] + j * step[i]) for i in range(3))
            for j in range(steps + 1)
        ]
        return grad



    @staticmethod
    def print_gradient(ascii_art, grad):
        width = os.get_terminal_size().columns
        output = []
        for i, line in enumerate(ascii_art.split('\n')):
            if i < len(grad):
                color = grad[i]
                output.append(f"\033[38;2;{color[0]};{color[1]};{color[2]}m{line}")
            else:
                output.append(line)
        return '\n'.join(output)

    @staticmethod
    def create(options, per_row=5):
        title_len = 30
        menu = []

        menu.append(f"╔{'╦'.join(['═' * title_len] * per_row)}╗")
        menu.append("")
        for i, opt in enumerate(options):
            if i % per_row == 0 and i != 0:
                menu[-1] += "║"
                menu.append(f"╠{'╬'.join(['═' * title_len] * per_row)}╣")
                menu.append("")

            padded_opt = f"[{str(i + 1).zfill(2)}] {opt.ljust(title_len - 7)}"
            if i % per_row == 0:
                menu[-1] += f"║ {padded_opt} "
            else:
                menu[-1] += f"║ {padded_opt} "

        remaining_slots = per_row - (len(options) % per_row)
        if remaining_slots != per_row:
            menu[-1] += f"║{' ' * title_len}" * remaining_slots + "║"

        menu.append(f"╚{'╩'.join(['═' * title_len] * per_row)}╝")
        return '\n'.join(menu)

    def center(self, text):
        lines = text.split('\n')
        terminal_width = os.get_terminal_size().columns
        centered_lines = [line.center(terminal_width) for line in lines]
        return '\n'.join(centered_lines)




    def run(self, login=True):
        os.system('cls')
        ascii_art = """



╔══════════════════════════════╗                                     ╦  ╦╔╦╗╦ ╦╦╦ ╦╔╦╗                                      ╔══════════════════════════════╗
║            gg/pop            ║                                     ║  ║ ║ ╠═╣║║ ║║║║                                      ║         Version: 5.3         ║
╚══════════════════════════════╝                                     ╩═╝╩ ╩ ╩ ╩╩╚═╝╩ ╩                                      ╚══════════════════════════════╝
"""

        result = self.create(self.options, 5)
        bot_name = self.bot_name[:10].ljust(10)
        guild_name = self.guild_name[:10].rjust(10)

        thing = f'{ascii_art}\n{result}'
        thing += f"""
╔════════════════════════════════════════╗                                                                        ╔════════════════════════════════════════╗
║ Bot -                    {bot_name}    ║                                                                        ║    {guild_name}                - Guild   ║
╚════════════════════════════════════════╝                                                                        ╚════════════════════════════════════════╝
                """
        
        if login == True:
            thing = f"""


╦  ╦╔╦╗╦ ╦╦╦ ╦╔╦╗
║  ║ ║ ╠═╣║║ ║║║║
╩═╝╩ ╩ ╩ ╩╩╚═╝╩ ╩

  (INFO):
  VER - {self.version}
  DSC - .gg/pop or .gg/CtctYGwBdz
  Made By - @realestneonic

"""
        grad = self.gradient(tuple(map(int, self.theme['start'].split(', '))), tuple(map(int, self.theme['end'].split(', '))), len(thing.split('\n')))
        colored = self.print_gradient(self.center(thing), grad)
        print(colored)


    def ChangeTheme(self):
        with open("db/themes.json", "r") as f:
            themes = json.load(f)
        cur = themes["loaded"]
        stuff = {}
        logger.inf("Current theme is" , name=str(cur))
        logger.inf("Theme List:")
        for theme in themes.keys():
            if theme != "loaded":
                logger.inf("Theme", name=theme)
                stuff[theme] = themes[theme]

        choice = logger.inp("Choice")
        if choice in themes.keys() and choice != "loaded":
            stuff["loaded"] = choice
            self.theme = themes[choice]
            with open('db/themes.json', 'w') as f:
                json.dump(stuff, f, indent=4)
            logger.inf("Theme changed to", name=choice)
        else:
            logger.inf("Error: Theme not found", name=choice)

        self.init()
