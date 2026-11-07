# This Python file uses the following encoding: utf-8
import typing
from pathlib import Path
from dataclasses import dataclass
from PySide6.QtGui import QColor

@dataclass
class cmap:
	map: list[QColor]
	def __init__(self, cdata = "", /, cm: typing.Union[list[QColor], str, Path] = None):
		pass

