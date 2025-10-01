import time
import threading
from . import ctime
from colorama import Fore

class Logger:
    """
    Logger. (Note: this class is repetitive ASF because i just used a script to make it automatically

    Attributes:
        - separator (str): Separator for the logger. Default is "● ".
        - format (str): Format of the logger. Can be "vertical" or "horizontal". Default is "vertical".
        - ctime (obj): The CTime class for logging time.
    """
    def __init__(self, separator=f"{Fore.LIGHTBLACK_EX}●{Fore.LIGHTWHITE_EX} ", format="vertical"):
        """
        Initializes a logger instance

        Parameters:
        - separator (str): Separator for the logger. Default is "● ".
        - format (str): Format of the logger. Can be "vertical" or "horizontal". Default is "vertical".
        """
        self.lock = threading.Lock()
        self.ctime = ctime.init()
        if format not in ["vertical", "horizontal"]:
            raise AttributeError(f"The given format '{format}' is not supported.")
        self.separator = f'{Fore.LIGHTBLACK_EX}{separator}{Fore.RESET}'
        self.format = format

    def llc(self, func, *args, **kwargs):
        with self.lock:
            return func(*args, **kwargs)

    def dbg(self, message, **kwargs):
        """
        Logs a debug message.

        Parameters:
        - message (str): Main content.
        - **kwargs: Additional {key} - value pairs.
        """
        return self.llc(self._dbg, message, **kwargs)

    def _dbg(self, message, **kwargs):
        timestamp = self.ctime.time()
        output = f"{timestamp} \x1b[38;2;200;255;200mDBG {self.separator}{Fore.LIGHTWHITE_EX}{message}"
        if self.format == "vertical":
            if len(kwargs) == 0:
                pass
            elif len(kwargs) >= 1:
                output += "\n"
                for index, (key, value) in enumerate(kwargs.items()):
                    {key} - f"{Fore.LIGHTBLACK_EX}{key[:15].capitalize():<15}\x1b[38;2;200;255;200m"
                    if index == len(kwargs) - 1:
                        output += f"{' ' * 8} \x1b[38;2;200;255;200m└ {Fore.LIGHTWHITE_EX}{key} {value}{Fore.RESET}\n"
                    else:
                        output += f"{' ' * 8} \x1b[38;2;200;255;200m├ {Fore.LIGHTWHITE_EX}{key} {value}{Fore.RESET}\n"
        elif self.format == "horizontal":
            clr = '\x1b[38;2;200;255;200m '
            output += f" {self.separator}{Fore.LIGHTWHITE_EX} {f' {Fore.LIGHTBLACK_EX}●{Fore.LIGHTWHITE_EX} '.join([f'{key} - ' + clr + f'{value}{Fore.RESET}' for key, value in kwargs.items()])}"
            print(output)

    def err(self, message, **kwargs):
        """
        Logs an error.

        Parameters:
        - message (str): Main content.
        - **kwargs: Additional {key} - value pairs.
        """
        return self.llc(self._err, message, **kwargs)

    def _err(self, message, **kwargs):
        timestamp = self.ctime.time()
        output = f"{timestamp} \x1b[38;2;255;200;200mERR {self.separator}{Fore.LIGHTWHITE_EX}{message}"
        if self.format == "vertical":
            if len(kwargs) == 0:
                pass
            elif len(kwargs) >= 1:
                output += "\n"
                for index, (key, value) in enumerate(kwargs.items()):
                    {key} - f"{Fore.LIGHTBLACK_EX}{key[:15].capitalize():<15}\x1b[38;2;255;200;200m"
                    if index == len(kwargs) - 1:
                        output += f"{' ' * 8} \x1b[38;2;255;200;200m└ {Fore.LIGHTWHITE_EX}{key} {value}{Fore.RESET}\n"
                    else:
                        output += f"{' ' * 8} \x1b[38;2;255;200;200m├ {Fore.LIGHTWHITE_EX}{key} {value}{Fore.RESET}\n"
        elif self.format == "horizontal":
            clr = '\x1b[38;2;255;200;200m '
            output += f" {self.separator}{Fore.LIGHTWHITE_EX} {f' {Fore.LIGHTBLACK_EX}●{Fore.LIGHTWHITE_EX} '.join([f'{key} - ' + clr + f'{value}{Fore.RESET}' for key, value in kwargs.items()])}"
        print(output)

    def inf(self, message, **kwargs):
        """
        Logs some info.

        Parameters:
        - message (str): Main content.
        - **kwargs: Additional {key} - value pairs.
        """
        return self.llc(self._inf, message, **kwargs)

    def _inf(self, message, **kwargs):
        timestamp = self.ctime.time()
        output = f"{timestamp} {Fore.LIGHTCYAN_EX}INF {self.separator}{Fore.LIGHTWHITE_EX}{message}"
        if self.format == "vertical":
            if len(kwargs) == 0:
                pass
            elif len(kwargs) >= 1:
                output += "\n"
                for index, (key, value) in enumerate(kwargs.items()):
                    {key} - f"{Fore.LIGHTBLACK_EX}{key[:15].capitalize():<15}{Fore.LIGHTCYAN_EX}"
                    if index == len(kwargs) - 1:
                        output += f"{' ' * 8} {Fore.LIGHTCYAN_EX}└ {Fore.LIGHTWHITE_EX}{key} {value}{Fore.RESET}\n"
                    else:
                        output += f"{' ' * 8} {Fore.LIGHTCYAN_EX}├ {Fore.LIGHTWHITE_EX}{key} {value}{Fore.RESET}\n"
        elif self.format == "horizontal":
            output += f" {self.separator}{Fore.LIGHTWHITE_EX} {f' {Fore.LIGHTBLACK_EX}●{Fore.LIGHTWHITE_EX} '.join([f'{key} - {Fore.LIGHTCYAN_EX}{value}{Fore.RESET}' for key, value in kwargs.items()])}"
        print(output)

    def wrn(self, message, **kwargs):
        """
        Logs a warning.

        Parameters:
        - message (str): Main content.
        - **kwargs: Additional {key} - value pairs.
        """
        return self.llc(self._wrn, message, **kwargs)

    def _wrn(self, message, **kwargs):
        timestamp = self.ctime.time()
        output = f"{timestamp} {Fore.LIGHTYELLOW_EX}WRN {self.separator}{Fore.LIGHTWHITE_EX}{message}"
        if self.format == "vertical":
            if len(kwargs) == 0:
                pass
            elif len(kwargs) >= 1:
                output += "\n"
                for index, (key, value) in enumerate(kwargs.items()):
                    {key} - f"{Fore.LIGHTBLACK_EX}{key[:15].capitalize():<15}{Fore.LIGHTYELLOW_EX}"
                    if index == len(kwargs) - 1:
                        output += f"{' ' * 8} {Fore.LIGHTYELLOW_EX}└ {Fore.LIGHTWHITE_EX}{key} {value}{Fore.RESET}\n"
                    else:
                        output += f"{' ' * 8} {Fore.LIGHTYELLOW_EX}├ {Fore.LIGHTWHITE_EX}{key} {value}{Fore.RESET}\n"
        elif self.format == "horizontal":
            output += f" {self.separator}{Fore.LIGHTWHITE_EX} {f' {Fore.LIGHTBLACK_EX}●{Fore.LIGHTWHITE_EX} '.join([f'{key} - {Fore.LIGHTYELLOW_EX}{value}{Fore.RESET}' for key, value in kwargs.items()])}"
        print(output)

    def ftl(self, message, **kwargs):
        """
        Logs a fatal error message and exits.

        Parameters:
        - message (str): Main content.
        - **kwargs: Additional {key} - value pairs.
        """
        return self.llc(self._ftl, message, **kwargs)

    def _ftl(self, message, **kwargs):
        timestamp = self.ctime.time()
        output = f"{timestamp} {Fore.RED}FTL {self.separator}{Fore.LIGHTWHITE_EX}{message}"
        if self.format == "vertical":
            if len(kwargs) == 0:
                pass
            elif len(kwargs) >= 1:
                output += "\n"
                for index, (key, value) in enumerate(kwargs.items()):
                    {key} - f"{Fore.LIGHTBLACK_EX}{key[:15].capitalize():<15}{Fore.RED}"
                    if index == len(kwargs) - 1:
                        output += f"{' ' * 8} {Fore.RED}└ {Fore.LIGHTWHITE_EX}{key} {value}{Fore.RESET}\n"
                    else:
                        output += f"{' ' * 8} {Fore.RED}├ {Fore.LIGHTWHITE_EX}{key} {value}{Fore.RESET}\n"
        elif self.format == "horizontal":
            output += f" {self.separator}{Fore.LIGHTWHITE_EX} {f' {Fore.LIGHTBLACK_EX}●{Fore.LIGHTWHITE_EX} '.join([f'{Fore.RED}{key} - {value}{Fore.RESET}' for key, value in kwargs.items()])}"
        print(output)
        time.sleep(10)
        exit(1)

    def inp(self, message, integer=False) -> str:
        """
        Asks for input and returns value.

        Parameters:
        - message (str): Message for input

        Returns:
        - answer (str): User input
        """
        return self.llc(self._inp, message, integer)

    def _inp(self, message, integer):
        timestamp = self.ctime.time()
        output = f"{timestamp} {Fore.RED}INP {self.separator}{Fore.LIGHTWHITE_EX}{message}\n"
        output += f"{' ' * 8} {Fore.RED}└ {Fore.LIGHTWHITE_EX}> {Fore.RESET}"
        if integer:
            while True:
                try:
                    answer = int(input(output))
                    break
                except ValueError:
                    self._err("Please enter a valid integer")
        else:
            answer= input(output).strip()

        print()
        return answer


def init(*args, **kwargs):
    return Logger(*args, **kwargs)
