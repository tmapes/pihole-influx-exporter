from os import getenv
from sys import stderr


def ensure_var_set(name: str):
    if not getenv(name):
        print(f"{name} not set!", file=stderr)
        exit(1)
