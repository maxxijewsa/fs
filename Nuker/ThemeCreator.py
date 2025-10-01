import tkinter as tk
from tkinter import colorchooser, simpledialog, messagebox
import json
import os
import random
import ctypes
from ttkbootstrap import Style

class Art:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ASCII Color Picker")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        self.start_color = (255, 255, 255)
        self.end_color = (0, 0, 0)
        self.db_file = "db/themes.json"

        self.init_widgets()
        self.draw()
        self.root.mainloop()

    def init_widgets(self):
        frame = tk.Frame(self.root, bg="#1e1e1e", padx=20, pady=20)
        frame.pack(expand=True, fill='both')

        tk.Label(frame, text="Start Color:", bg="#1e1e1e", fg="#ffffff", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.start_btn = self.create_button(frame, "color", self.pick_start)
        self.start_btn.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        tk.Label(frame, text="End Color:", bg="#1e1e1e", fg="#ffffff", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.end_btn = self.create_button(frame, "color", self.pick_end)
        self.end_btn.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

        self.create_button(frame, "Save Theme", self.save_theme).grid(row=3, column=0, columnspan=2, pady=10)
        self.create_button(frame, "Random Theme", self.random_theme).grid(row=4, column=0, columnspan=2, pady=10)

    def create_button(self, parent, text, command):
        button = tk.Button(parent, text=text, command=command, bg="#007bff", fg="#ffffff", font=("Arial", 12), relief="flat", borderwidth=0)
        button.config(pady=10, padx=20)
        return button

    def pick_start(self):
        color = colorchooser.askcolor(title="Start Color")[0]
        if color:
            self.start_color = tuple(map(int, color))
            self.start_btn.config(bg=self.rgb_to_hex(self.start_color))
            self.draw()

    def pick_end(self):
        color = colorchooser.askcolor(title="End Color")[0]
        if color:
            self.end_color = tuple(map(int, color))
            self.end_btn.config(bg=self.rgb_to_hex(self.end_color))
            self.draw()

    def random_theme(self):
        self.start_color = tuple(random.randint(0, 255) for _ in range(3))
        self.end_color = tuple(random.randint(0, 255) for _ in range(3))
        self.start_btn.config(bg=self.rgb_to_hex(self.start_color))
        self.end_btn.config(bg=self.rgb_to_hex(self.end_color))
        self.draw()

    def rgb_to_hex(self, rgb):
        return "#%02x%02x%02x" % rgb

    def draw(self):
        art = self.art()
        os.system('cls' if os.name == 'nt' else 'clear')
        grad = self.gradient(self.start_color, self.end_color, len(art.split('\n')))
        for i, line in enumerate(art.splitlines()):
            color = grad[i % len(grad)]
            print(f"\033[38;2;{color[0]};{color[1]};{color[2]}m{line}")

    def save_theme(self):
        name = simpledialog.askstring("Save Theme", "Name:")
        if not name:
            return

        if os.path.exists(self.db_file):
            with open(self.db_file, "r") as file:
                data = json.load(file)
        else:
            data = {}

        if name in data:
            messagebox.showerror("Error", "Theme name already exists")
            return

        data[name] = {
            "start": f"{self.start_color[0]}, {self.start_color[1]}, {self.start_color[2]}",
            "end": f"{self.end_color[0]}, {self.end_color[1]}, {self.end_color[2]}"
        }

        with open(self.db_file, "w") as file:
            json.dump(data, file, indent=4)

        messagebox.showinfo("Success", "Theme saved.")

    @staticmethod
    def gradient(start, end, steps):
        step = [(end[i] - start[i]) / steps for i in range(3)]
        return [tuple(int(start[i] + j * step[i]) for i in range(3)) for j in range(steps + 1)]

    @staticmethod
    def art():
        return r"""




                      ╔══════════════════════════════╗                                     ╦  ╦╔╦╗╦ ╦╦╦ ╦╔╦╗                                      ╔══════════════════════════════╗
                      ║            gg/pop            ║                                     ║  ║ ║ ╠═╣║║ ║║║║                                      ║         Version: 5.4         ║
                      ╚══════════════════════════════╝                                     ╩═╝╩ ╩ ╩ ╩╩╚═╝╩ ╩                                      ╚══════════════════════════════╝

                      ╔══════════════════════════════╦══════════════════════════════╦══════════════════════════════╦══════════════════════════════╦══════════════════════════════╗
                      ║ [01] Create Channels         ║ [02] Delete Channels         ║ [03] Lock Channels           ║ [04] Unlock Channels         ║ [05] Rename Channels         ║
                      ╠══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╣
                      ║ [06] Shuffle Channels        ║ [07] Spam All Channels       ║ [08] Webhook Spam Channels   ║ [09] Create Roles            ║ [10] Delete Roles            ║
                      ╠══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╣
                      ║ [11] Grant Role              ║ [12] Rename Roles            ║ [13] Grant Admin             ║ [14] Grant Everyone Admin    ║ [15] Mass Ban                ║
                      ╠══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╣
                      ║ [16] Mass Kick               ║ [17] Prune Members           ║ [18] Mass Nick               ║ [19] Mass DM                 ║ [20] Delete Emojis           ║
                      ╠══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╣
                      ║ [21] Create Emojis           ║ [22] Change Server Name      ║ [23] Leave Guild             ║ [24] Leave All Guilds        ║ [25] Full Nuke               ║
                      ╠══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╣
                      ║ [26] Guild Info              ║ [27] Get Invite Link         ║ [28] Unban User              ║ [29] Unban All Users         ║ [30] Scrape Servers          ║
                      ╠══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╣
                      ║ [31] Change Guild            ║ [32] Change Theme            ║ [33] Credits                 ║ [34] RPS Check               ║ [35] Exit                    ║
                      ╠══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╬══════════════════════════════╣
                      ║ [36] Coming Soon             ║                              ║                              ║                              ║                              ║
                      ╚══════════════════════════════╩══════════════════════════════╩══════════════════════════════╩══════════════════════════════╩══════════════════════════════╝
                      ╔════════════════════════════════════════╗                                                                        ╔════════════════════════════════════════╗
                      ║ Bot -                    bot1273970    ║                                                                        ║           sex                - Guild   ║
                      ╚════════════════════════════════════════╝                                                                        ╚════════════════════════════════════════╝

11:42:32 INP ● Option
         └ >
"""

if __name__ == "__main__":
    os.system('mode con: cols=200 lines=40')
    ctypes.windll.kernel32.SetConsoleTitleW("Lithium | V5 | Ascii Art Gen                   [discord.gg/pop]")
    Art()
