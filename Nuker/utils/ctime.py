from colorama import Fore
from datetime import datetime

class CTime:
    """
    Time management BS.

    Attributes:
        started (datetime obj): The time when we have initialized the class.
    """

    def __init__(self):
        """
        Initializes CTime class.
        """
        self.started = datetime.now()

    def time(self, color=True) -> str:
        """
        Returns the current time in "HH:MM:SS"
        """
        if color:
            return f"{Fore.LIGHTBLACK_EX}{datetime.now().strftime('%H:%M:%S')}{Fore.RESET}"
        else:
            return datetime.now().strftime('%H:%M:%S')

    def elapsed(self) -> str:
        """
        Gets elapsed time based on the started attribute.

        Returns:
            str: Elapsed time in "HH:MM:SS"
        """
        current = datetime.now()
        diff = current - self.started
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

def init():
    return CTime()
