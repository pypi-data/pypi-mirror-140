from injectable import injectable
import random
from string import ascii_lowercase, ascii_uppercase
from user_agent import generate_user_agent


@injectable
class UtilsRandom:
    def __init__(self):
        self.CHARS_ASCII = []
        self.CHARS_ASCII.extend(ascii_lowercase)
        self.CHARS_ASCII.extend(ascii_uppercase)

    def get_random_string(self, size: int) -> str:
        return ''.join([random.choice(self.CHARS_ASCII) for i in range(0, size)])

    def get_random_user_agent(self) -> str:
        return str(generate_user_agent())

    def get_random_ip(self) -> str:
        return '.'.join([str(random.randint(0,255)) for i in range(0,4)])
