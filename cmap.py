# This Python file uses the following encoding: utf-8
import math
from dataclasses import dataclass
import re
from PySide6.QtGui import QColor

# lerp, inv_lerp, and remap from
# https://gist.github.com/laundmo/b224b1f4c8ef6ca5fe47e132c8deab56

def lerp(a: float, b: float, t: float) -> float:
	"""Linear interpolate on the scale given by a to b, using t as the point on that scale.
	Examples
	--------
		50 == lerp(0, 100, 0.5)
		4.2 == lerp(1, 5, 0.8)
	"""
	return (1 - t) * a + t * b

def inv_lerp(a: float, b: float, v: float) -> float:
	"""Inverse Linar Interpolation, get the fraction between a and b on which v resides.
	Examples
	--------
	  0.5 == inv_lerp(0, 100, 50)
	  0.8 == inv_lerp(1, 5, 4.2)
	"""
	try:
		return (v - a) / (b - a)
	except ZeroDivisionError:
		return 0

def remap(i_min: float, i_max: float, o_min: float, o_max: float, v: float) -> float:
	"""Remap values from one linear scale to another, a combination of lerp and inv_lerp.
	i_min and i_max are the scale on which the original value resides,
	o_min and o_max are the scale to which it should be mapped.
	Examples
	--------
		45 == remap(0, 100, 40, 50, 50)
		6.2 == remap(1, 5, 3, 7, 4.2)
	"""
	return lerp(o_min, o_max, inv_lerp(i_min, i_max, v))


def rgb_from_hex(code):
	rgb = tuple(int(code[i:i+2], 16) for i in (0, 2, 4))
	return QColor.fromRgb(rgb[0], rgb[1], rgb[2])

def lerpColors(a: QColor, b: QColor, t: float):
	return QColor.fromRgbF(*(lerp(ca, cb, t) for ca,cb in zip(a.getRgbF(), b.getRgbF())))

@dataclass
class cmap:
	map: list[QColor]
	def interpolate(self, val):
		t,i = math.modf(val*(len(self.map)-1))
		if 0 <= i < len(self.map)-1:
			lower,upper = self.map[int(i):int(i)+2]
			#print(f"{lower}, {upper}, {t}")
			return lerpColors(lower, upper, t)
		elif i < 0:
			return self.map[0]
		else:
			return self.map[-1]
		pass
	def __getitem__(self, i):
		return self.map[i]
	def __iter__(self):
		return self.map.__iter__()
	def __len__(self):
		return len(self.map)
	def __reversed__(self):
		return cmap(list(reversed(self.map)))


_ws = re.compile('[ \t\r\n]+')
_num = re.compile('[0-9a-fA-F]+')

def from_str(cdata):
	# first span is a comment
	spans = cdata.split(':')
	ret = {}
	for i in range(1, len(spans), 2):
		name = spans[i]
		#tokens = re.findall(_num, spans[i+1])
		tokens = re.split(_ws, spans[i+1])
		length = int(tokens[0])
		colors = [rgb_from_hex(s) for s in tokens[1:] if s]
		assert(length == len(colors))
		ret |= {name: cmap(colors)}
	return ret

def from_file(path):
	with open(path, 'r') as file:
		return from_str(file.read())
