from flask import send_from_directory
from windowbox import AppPath


class StaticHandler():
    @classmethod
    def get_file(filename):
        return send_from_directory(AppPath.static(), filename)
