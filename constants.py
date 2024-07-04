from typing import Tuple
import enum
import sys
import pickle
import os

COLOR = str
POSITION = Tuple[int, int]


class Settings:
    def __init__(self):
        self.running = True
        self.scan_directory = None
        self.source_directory = None
        self.find_by = None
        self.file_types = None
        self._open()

    def save(self):
        with open(SETTINGS_PATH, 'wb+') as my_file:
            my_file.write(pickle.dumps(self._value))

    def _open(self):
        try:
            with open(SETTINGS_PATH, 'rb') as my_file:
                self._value = pickle.loads(my_file.read())
        except (FileNotFoundError, ValueError):
            self._value = DEFAULT_SETTINGS

    def reset(self):
        os.remove(SETTINGS_PATH)
        self._open()

    @property
    def _value(self):
        return self.scan_directory, self.source_directory, self.find_by, self.file_types

    @_value.setter
    def _value(self, value):
        self.scan_directory, self.source_directory, self.find_by, self.file_types = value


class Keycodes(enum.IntEnum):
    A = 65
    SHIFT = 16
    ESCAPE = 27
    LEFT = 37
    UP = 38
    RIGHT = 39
    DOWN = 40
    DELETE = 46


class Color(enum.StrEnum):
    BLACK: COLOR = '#000000'
    RED: COLOR = '#FF0000'
    GREEN: COLOR = '#00FF00'
    BLUE: COLOR = '#0000FF'
    WHITE: COLOR = '#FFFFFF'
    YELLOW: COLOR = '#FFFF00'
    GRAY: COLOR = '#808080'


class Modifiers(enum.Enum):
    SHIFT = 'SHIFT'
    CAPS_LOCK = 'CAPS_LOCK'
    CTRL = 'CTRL'
    LEFT_ALT = 'LEFT_ALT'
    MUN_LOCK = 'MUN_LOCK'
    RIGHT_ALT = 'RIGHT_ALT'
    MOUSE_LEFT = 'MOUSE_LEFT'
    MOUSE_MID = 'MOUSE_MID'
    MOUSE_RIGHT = 'MOUSE_RIGHT'
    SCROLL_LOCK = 'SCROLL_LOCK'


class Status(enum.IntEnum):
    REST = 0
    SCAN = 1
    FINISH_SCAN = 2


class FindBy(enum.IntEnum):
    FULL_NAME = 0
    START_NAME = 1


class FileTypes(enum.Enum):
    IMAGE = {'jpg', 'png', 'gif', 'webp', 'tiff', 'psd', 'raw', 'bmp', 'heif', 'jpeg'}
    VIDEO = {'mp4', 'mov', 'wmv', 'avi', 'avchd', 'mkv', 'webm'}
    DOCUMENT = {'doc', 'docx', 'pdf', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'}
    APP = {'exe', 'apk', 'bat', 'bin', 'com', 'wsf', 'py', 'c', 'java', 'cs', 'php', 'swift', 'vb'}
    FOLDER = {'', 'zip', 'rar', 'tgz'}
    AUDIO = {'mp3', 'wma', 'ogg', 'wpl', 'wav', 'mid', 'midi'}


MODIFIER_KEYS = {Modifiers.SHIFT: 1,
                 Modifiers.CAPS_LOCK: 2,
                 Modifiers.CTRL: 4,
                 Modifiers.MUN_LOCK: 8,
                 Modifiers.SCROLL_LOCK: 32,
                 Modifiers.MOUSE_LEFT: 256,
                 Modifiers.MOUSE_MID: 512,
                 Modifiers.MOUSE_RIGHT: 1048,
                 Modifiers.LEFT_ALT: 131072,
                 Modifiers.RIGHT_ALT: 131080}
FILE_TYPES = [FileTypes.IMAGE,
              FileTypes.VIDEO,
              FileTypes.DOCUMENT,
              FileTypes.APP,
              FileTypes.FOLDER,
              FileTypes.AUDIO]

DEF_TEXT_FONT = 'Helvetica'
DEF_TEXT_SIZE = 12
DEF_TEXT_COLOR = None
DEF_TEXT_BG_COLOR = None
SCREEN_SIZE = '1000x500'
SCREEN_TITLE = 'EZ Search'


FILE_PATH = r'file.txt'
SETTINGS_PATH = r'settings.txt'


DEFAULT_SETTINGS = [sys.argv[0][:3], sys.argv[0][:3], FindBy.FULL_NAME, [1]*(len(FILE_TYPES)-1)]

settings = Settings()
