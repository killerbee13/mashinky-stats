# This Python file uses the following encoding: utf-8
from enum import Enum, auto
from pathlib import Path
import math
import re
import types
import typing
from typing import Any, Optional, Type, TypeVar
from dataclasses import dataclass

from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel
#from PySide6.QtWidgets import

import constants as C

class _default:
	def __bool__(self):
		return False
Default = _default()
_default.__new__ = lambda self, *args: Default
_default.__call__ = lambda self, *args: Default
otherwise = lambda a, b: a if a is not Default else b
T = TypeVar('T')
safe_div = lambda a, b: a/b if b else 0.
class Disp(Enum):
	Null = 0
	Positive = auto()
	Negative = auto()
	Parity = auto()

@dataclass
class FieldBase:
	annotation: Type
	csv: Optional[str]
	tbl: Optional[str]
	owner: Any = None
	disp: Disp = Disp.Null
	bin : Any = None
	_key_name: str = None
	def __set_name__(self, owner, name):
		if not isinstance(owner, type):
			object.__setattr__(self, 'owner', owner)
		object.__setattr__(self, '_key_name', name)
	def _key(self):
		return f"key-{self._key_name}"
	def __init__(self, U: Type, csv: Optional[str], tbl: Optional[str],
		disp: Disp = Default, bin: Any = None):
		object.__setattr__(self, 'csv', csv)
		object.__setattr__(self, 'tbl', otherwise(tbl, csv))
		object.__setattr__(self, 'annotation', U)
		if disp is Default:
			if U is float or U is int or float in typing.get_args(U) or int in typing.get_args(U):
				object.__setattr__(self, 'disp', Disp.Positive)
		else:
			object.__setattr__(self, 'disp', disp)
		object.__setattr__(self, 'bin', bin)
@dataclass
class KeyBase(FieldBase):
	xml: Optional[str] = None
	def __init__(self, U: Type, csv: Optional[str], tbl: Optional[str],
		xml: Optional[str] = None, disp: Disp = Default, bin: Any = None):
		super().__init__(U, csv, tbl, disp, bin)
		object.__setattr__(self, 'xml', xml)
		object.__setattr__(self,'_key_name', csv)

def field(U: Type, csv: Optional[str], tbl: Optional[str] = Default, /,
	xml : Optional[str] = None, default: Optional[T] = Default,
	disp: Disp = Default, bin: Any = None):
	"""def field(U: Type, csv: Optional[str], tbl: Optional[str] = csv, /,
		xml : Optional[str] = None, default : Optional[T] = Default
		disp: Disp = Disp.Positive):
	If only csv is specified, tbl reuses that value. If default is specified,
	the field has that as its default value, otherwise there is no default."""
	# name lookup gets confused by the class shadowing the closure-captured args
	class Key(KeyBase):
		owner = None
		def __init__(self):
			super().__init__(U, csv, tbl, xml, disp, bin)
		def __set_name__(self, owner, name):
			super().__set_name__(owner, name)
			if default is not Default:
				if type(default) is U or type(default) in typing.get_args(U) or U is Any:
					object.__setattr__(self, 'default', default)
				else:
					object.__setattr__(self, 'default', U(default))
				#print(f"setting default={repr(default)}, csv={csv_}, tbl={tbl_}")
				#object.__setattr__(self, 'default', default)
			else:
				object.__setattr__(self, 'default', Default)
			owner.__annotations__[name] = U
		def is_default(self, *args):
			if not args:
				return default is not Default
			else:
				return (self._key() not in args[0].__dict__
					and default is not Default)
		def __repr__(self):
			if self.owner:
				try:
					value = self.__get__(self.owner, type(self.owner))
					return f"<Key {self._key_name}={repr(value)}>"
				except AttributeError:
					return f"<Key {self._key_name}=unset>"
			else:
				return (f"<Key '{self._key_name}'({repr(self.csv)}, "
					f"{repr(self.tbl)}, xml={repr(self.xml)}"
					+ (f", default={repr(default)})>" if default is not Default else ")>"))
		def __set__(self, obj, value):
			#print(repr(self), repr(obj), repr(value), sep=';')
			obj.__dict__[self._key()] = value
			obj._gen_cache = {}
		def __setattr__(self, name, value):
			raise AttributeError(f"Key.{name}={value}: Keys are immutable")
		def __delattr__(self, name):
			raise AttributeError(f"del Key.{name}: Keys are immutable")
	#def fmt_key(k):
	#	if k.is_default():
	#		return f"Key({self._key_name}, {repr(k.csv)}, {repr(k.tbl)}, xml={repr(k.xml)}, default={repr(k.default)}, owner={repr(k.owner)})"
	#	else:
	#		return f"Key({self._key_name}, {repr(k.csv)}, {repr(k.tbl)}, xml={repr(k.xml)}, owner={repr(k.owner)})"
	if default is Default:
		def __get__(self, obj, owner=None):
			#print(fmt_key(self), f"<class {repr(type(obj).__name__)}>", repr(owner), sep=';')
			try:
				return obj.__dict__[self._key()]
			except KeyError as e:
				raise AttributeError(
					f"'{owner.__name__}' field '{self._key_name}' unset") from e
			except AttributeError:
				return self
		Key.__get__ = __get__
	else:
		def __get__(self, obj, owner=None):
			#print(fmt_key(self), f"<class {repr(type(obj).__name__)}>", repr(owner), sep=';')
			try:
				return obj.__dict__.get(self._key(), self.default)
			except AttributeError:
				return self
		Key.__get__ = __get__
	return Key()
def default_field(*args, **kwargs):
	return field(*args, default=None, **kwargs)
def zero_field(*args, **kwargs):
	return field(*args, default=0, **kwargs)
def table_field(U: T, tbl: str, /, xml : Optional[str] = None,
	default: Optional[T] = Default, **kwargs):
	"""For fields which are not in the CSV but are in the table"""
	return field(U, None, tbl, xml=xml, default=default, **kwargs)
def xml_field(U: T, xml : Optional[str] = None, /, tbl: str = Default,
	default: Optional[T] = Default, **kwargs):
	"""Non-CSV fields"""
	return field(U, None, tbl, xml=xml, default=default, **kwargs)
def zero_xml_field(U: T, xml : Optional[str] = None, /, tbl: str = Default, **kwargs):
	return field(U, None, tbl, xml=xml, default=0, **kwargs)
def default_xml_field(U: T, xml : Optional[str] = None, /, tbl: str = Default, **kwargs):
	return field(U, None, tbl, xml=xml, default=None, **kwargs)

def generated(first, *args, **kwargs):
	"""Generates a field from others. Cannot have an xml key.
	generated(fun: types.FunctionType, csv: Optional[str], tbl: Optional[str] = Default):
		Value of obj.gen is computed as fun(obj). tbl defaults to csv
	@generated(csv: str, tbl: Optional[str] = Default):
		decorator version of the above"""
	def impl(fun: types.FunctionType, csv: Optional[str],
		tbl: Optional[str] = Default, result=None, cache=True, disp=Default, bin=None):
		class Gen(FieldBase):
			owner = None
			def __init__(self):
				super().__init__(result, csv, tbl, disp, bin)
			def is_default(self, *args):
				return True
			def __repr__(self):
				#print(f"<Gen '{self._key_name}'('{self.csv}', '{self.tbl}')>")
				if self.owner:
					try:
						value = self.__get__(self.owner, type(self.owner))
						return f"<Gen {self._key_name}={repr(value)}>"
					except AttributeError:
						return f"<Gen {self._key_name}=unset>"
				else:
					return f"<Gen '{self._key_name}'('{self.csv}', '{self.tbl}')>"
			def __set__(self, obj, value):
				raise AttributeError(f"{obj}.key-{self._key_name}={value}: Generated fields cannot be assigned")
			def __setattr__(self, name, value):
				raise AttributeError(f"Gen.{name}={value}: Gens are immutable")
			def __delattr__(self, name):
				raise AttributeError(f"del Gen.{name}: Gens are immutable")
		if cache:
			def __get__(self, obj, owner=None):
				#print(repr(self), repr(obj), repr(owner), sep=';')
				try:
					return obj._gen_cache[self._key_name]
				except KeyError:
					ret = fun(obj)
					obj._gen_cache[self._key_name] = ret
					return ret
				except AttributeError:
					return self
			Gen.__get__ = __get__
		else:
			def __get__(self, obj, owner=None):
				#print(repr(self), repr(obj), repr(owner), sep=';')
				if obj is not None:
					return fun(obj)
				else:
					return self
			Gen.__get__ = __get__
		return Gen()
	if type(first) is str or type(first) is None:
		return lambda f: impl(f, first, *args, **kwargs)
	elif callable(first):
		return impl(first, *args, **kwargs)
	else:
		raise TypeError(f"generated expects a function, got {repr(first)}")

class Cost(dict[str, float]):
	pass

def finalize(cls):
	def subscript(self, field):
		if isinstance(cls.__dict__[field], FieldBase):
			return self.__getattribute__(field)
		else:
			raise KeyError(f"{repr(field)} not in {cls.__name__}")
	cls.__getitem__ = subscript
	def get(self, field, fallback=None):
		try:
			return self[field]
		except AttributeError:
			return fallback
	cls.get = get
	def contains(self, field):
		if field not in cls.__dict__:
			return False
		elif cls.__dict__[field].is_default():
			return True
		elif cls.__dict__[field]._key() in self.__dict__:
			return True
		else:
			return False
	cls.__contains__ = contains
	def is_default(self, field):
		return cls.__dict__[field].is_default(self)
	cls.is_default = is_default
	def field_rep(self, field):
		if field in self:
			if self.is_default(field):
				return f"Default({repr(self[field])})"
			else:
				return repr(self[field])
		else:
			return "unset"
	cls.field_rep = field_rep
	def rep(self):
		rep = ", ".join((f"{k[0]}={self.field_rep(k[0])}" for k in dict(cls.__dict__).items()
			if isinstance(k[1], KeyBase) and k[0] in self))
		return f"{type(self).__name__}({rep})"
	cls.__repr__ = rep
	#def field_str(self, field):

	init_fields = {}
	out_fields = {}
	for k,v in dict(cls.__dict__).items():
		if isinstance(v, FieldBase):
			f = {'csv': v.csv, 'tbl': v.tbl}
			if isinstance(v, KeyBase):
				f |= {'xml': v.xml}
				if v.is_default():
					f |= {'default': v.default}
				init_fields |= {k: f}
			out_fields |= {k: f}
	#print(repr(init_fields))
	#print(repr(out_fields))

	def assign_args(self, /, strict=False, **kwargs):
		fields = init_fields.copy()
		for k,v in kwargs.items():
			if k in fields:
				if v is not Default:
					self.__setattr__(k, cls.__annotations__[k](v))
					del fields[k]
				else:
					if not cls.__dict__[k].is_default():
						raise ValueError()
			else:
				# unexpected kwargs
				raise ValueError(f"{cls.__name__}.assign_args(): "\
			f"unexpected keyword argument {k}={repr(v)}")
		if strict:
			return dict(filter(lambda f: 'default' not in f[1], fields.items()))
		else:
			return None
	cls.assign_args = assign_args
	def init(self, strict=False, **kwargs):
		self._gen_cache = {}
		fields = self.assign_args(strict=strict, **kwargs)
		if fields:
			raise ValueError(f"{cls.__name__}.from_args(): "\
				f"missing required keyword arguments {list(fields.keys())}")
	def from_args(cls, /, strict=False, **kwargs):
		r = cls()
		init(r)
		return r
	cls.from_args = classmethod(from_args)
	if '__init__' not in cls.__dict__:
		cls.__init__ = init
	def from_(attr, fields_):
		def impl(cls, obj_, /, strict=False, **kwargs):
			fields = fields_.copy()
			obj = obj_.copy()
			r = cls()
			for k,v in obj.copy().items():
				for f,ks in fields.items():
					if ks[attr] == k:
#						if type(self.default) is U or type(self.default) in typing.get_args(U):
#							return self.default
#						else:
#							return U(self.default)
						U = cls.__annotations__[f]
						if type(v) is U or type(v) in typing.get_args(U) or U is Any:
							r.__setattr__(f, v)
						else:
							r.__setattr__(f,U(v))
						# safe because the loop ends at the break
						del fields[f]
						# safe because of the copy() call
						del obj[k]
						break
				else:
					# unexpected key
					pass
			# unexpected keys
			if obj:
				pass
			f2 = r.assign_args(strict=strict, **kwargs)
			if strict:
				# missing keys
				to_see = []
				# fields currently holds all fields which were not in obj
				# f2 holds all fields not in kwargs
				for k,v in fields.items():
					if not cls.__getattribute__(v).is_default() and k in f2:
						to_see.append(k)
				if to_see:
					raise ValueError(f"{cls.__name__}.from_{attr}(): "\
						f"missing required keyword arguments {to_see}")
			return r
		return impl
	cls.from_csv = classmethod(from_('csv', init_fields))
	cls.from_xml = classmethod(from_('xml', init_fields))
	def to_(attr):
		def impl(self, all=True):
			out = {}
			for f,ks in out_fields.items():
				if ks.get(attr) is not None and f in self and (
					all or not self.is_default(f)):
					out |= {ks[attr]: self[f]}
			return out
		return impl
	cls.to_csv = to_('csv')
	cls.to_xml = to_('xml')
	def asdict(self, all=True):
		out = {}
		for f,ks in out_fields.items():
			if f in self and (all or not self.is_default(f)):
					out |= {f: self[f]}
		return out
	cls.asdict = asdict
	def keys():
		return list(out_fields)
	cls.keys = staticmethod(keys)
	return cls

@finalize
class test:
	x = field(int, "x")
	y = field(int, "y", xml="y")
	z = field(int, "z", default=3)
	w = field(int, "w", xml="w", default=4)

@finalize
class Row:
	# XML/core properties: (in XML, shown in game, or very trivially derived)
	#   Common:
	name = field(str, C.NAME, xml='name')
	index = table_field(int, 'Index', disp=Disp.Null)
	source = field(Path, 'source', C.SOURCE, default='')
	vanilla = table_field(bool, C.VANILLA, default=False)
	id = field(str, 'id', 'ID', xml=C.ID, default='')
	cid = default_field(Optional[str], C.CID, 'Cargo ID', xml='cargo')
	vehicle_type = table_field(int, 'vehicle_type', xml='vehicle_type', disp=Disp.Null)
	track = zero_field(int, None, C.TRACK, xml='track', disp=Disp.Null)
	weight_full = field(float, C.WEIGHT_FULL, xml='weight_full', disp=Disp.Negative)
	weight_empty = field(float, C.WEIGHT_EMPTY, xml='weight_empty', disp=Disp.Negative)
	epoch = field(str, C.EPOCHS, xml='epoch', default='')
	eras = generated(lambda r: parse_eras(r.epoch), C.ERAS)
	era = generated(lambda r: r.eras[0], C.ERA, result=int, disp=Disp.Null)

	icon = xml_field(str, 'icon', default="")
	icon_texture = xml_field(str, 'icon_texture', default="")
	icon_color = xml_field(str, 'icon_color', default="")

	length_b = zero_xml_field(float, 'length')
	length_head = zero_xml_field(float, 'head_length')
	length_tail = zero_xml_field(float, 'tail_length')
	length = generated(lambda r: r.length_b + r.length_head + r.length_tail, C.LENGTH, result=float, disp=Disp.Negative)

	#   Prime movers:
	power = field(float, C.POWER, xml='power', default=0.)
	max_speed = field(float, C.SPEED, xml='max_speed', default=0.)
	max_speed_mph = generated(lambda r: r.max_speed/C.KM_PER_MI, C.SPEED_MPH, result=float)
	max_speed_reverse = zero_field(Any, None, "Reverse speed (km/hr)", xml='max_speed_reverse')
	@generated("Reverse speed (mph)")
	def max_speed_reverse_mph(self):
		if type(self.max_speed_reverse) is float:
			return round(self.max_speed_reverse/C.KM_PER_MI)
		else:
			return self.max_speed_reverse
	weight = generated(lambda r: r.weight_full, C.WEIGHT, result=float, disp=Disp.Negative)

	#   Trains:
	@generated(C.TRACTION, result=float, disp=Disp.Positive)
	def traction(self):
		return math.floor(safe_div(self.power*C.TRACTION_SCALE, self.max_speed))
	towage = generated(lambda r: r.traction - r.weight_full, C.TOWAGE, result=float)
	throughput = generated(lambda r: r.towage*r.max_speed, C.THROUGHPUT, result=float)

	# Fuel
	raw_cost = table_field(str, None, xml='fuel_cost', default='')
	cost = generated(lambda r: costs(r.raw_cost), C.COSTS_RAW)
	cash = generated(lambda r: r.cost.get(C.CASH, 0.), C.CASH, tbl="Money", result=float, disp=Disp.Negative)
	coal = generated(lambda r: r.cost.get(C.COAL, 0.), C.COAL, result=float, disp=Disp.Negative)
	diesel = generated(lambda r: r.cost.get(C.DIESEL, 0.), C.DIESEL, result=float, disp=Disp.Negative)
	electric = generated(lambda r: r.cost.get(C.ELECTRIC, 0.), C.ELECTRIC, result=float, disp=Disp.Negative)
	adjcost = generated(lambda r: cost_adj(r.cost), C.ADJCOST, tbl="Adjusted Cost", cache=False, result=float, disp=Disp.Negative)

	#   Cargo carriers:
	capacity = zero_field(int, C.CARGO, xml='capacity')
	@generated(C.TYPE)
	def ctype(self):
		ct = cargo_by_label.get(self.cid) or ""
		if self.vehicle_type == 0 and self.power:
			if ct == C.PASSENGER:
				return "Pass. Engine"
			elif ct == C.MAIL:
				return "Mail Engine"
		return ct
	raw_effect = xml_field(str, 'effect', default="")
	@generated('Effect')
	def effect(self):
		effect = re.fullmatch(r'(?:profit\[[^]]*\])\*([0-9]*.?[0-9]*)',
			self.raw_effect)
		if effect:
			return float(effect.group(1))
		else:
			return 1
	@generated(C.BONUS, result=float)
	def bonus(self):
		effect = re.fullmatch(r'(?:profit\[[^]]*\])\*([0-9]*.?[0-9]*)',
			self.raw_effect)
		if effect:
			return round(100*(float(effect.group(1))-1))
		else:
			return ''

	# Ratios and composites:
	#   Prime movers:
	pwt_empty = generated(lambda r: r.power/r.weight_empty, C.PWT_EMPTY, result=float)
	pwt_full = generated(lambda r: safe_div(r.power, r.weight_full), C.PWT_FULL, result=float)
	power_per_length = generated(lambda r: r.power/r.length, C.POWER_PER_LENGTH, result=float)

	#   Trains:
	pwt_loaded = generated(lambda r: safe_div(r.power, r.traction), C.PWT_FULL, result=float)
	tow_per_length = generated(lambda r: r.towage/r.length, C.TOW_PER_LENGTH, result=float)

	#   Cargo carriers:
	profit = generated(lambda r: r.capacity*r.effect, C.PROFITABILITY, result=float)
	cargo_per_length = generated(lambda r: r.capacity/r.length, C.CARGO_PER_LENGTH, result=float)
	profit_per_length = generated(lambda r: r.profit/r.length, C.PROFIT_PER_LENGTH, result=float)
	cargo_per_wt = generated(lambda r: 10*r.capacity/r.weight_full, C.CARGO_PER_WT, result=float)
	profit_per_wt = generated(lambda r: 10*r.profit/r.weight_full, C.PROFIT_PER_WT, result=float)

	#   Units: (i.e. power and capacity both != 0)
	cargo_throughput = generated(lambda r: r.capacity*r.max_speed, C.TP_CARGO, result=float)
	profit_throughput = generated(lambda r: r.profit*r.max_speed, C.TP_PROFIT, result=float)

	#   Fuel:
	def _TP1(self, c: str, t: float) -> float:
		if self.power and self.cost.get(c):
			return t/(self.cost.get(c, 0)*fixed_scale[c])
		else:
			return ''
	def _TP_ac(self, t: float) -> float:
		return self.adjcost and t/(self.adjcost*adj_scale)
	def _TP(self, cur: str) -> float:
		return self._TP1(cur, self.throughput)
	def _TPc(self, cur: str) -> float:
		return self._TP1(cur, self.cargo_throughput)
	def _TPp(self, cur: str) -> float:
		return self._TP1(cur, self.profit_throughput)

	#   Train-specific
	CD6 = generated(lambda r: r.towage/(6-r.length), C.CD6, result=float)
	CD8 = generated(lambda r: r.towage/(8-r.length), C.CD8, result=float)

	TP_adjcost = generated(lambda r: r._TP_ac(r.throughput), C.TP_ADJCOST, cache=False, result=float)
	TP_cash = generated(lambda r: r._TP(C.CASH), C.TP_CASH, tbl="TP/Money", result=float)
	TP_coal = generated(lambda r: r._TP(C.COAL), C.TP_COAL, result=float)
	TP_diesel = generated(lambda r: r._TP(C.DIESEL), C.TP_DIESEL, result=float)
	TP_electric = generated(lambda r: r._TP(C.ELECTRIC), C.TP_ELECTRIC, result=float)

	#   Unit-specific
	TPc_adjcost = generated(lambda r: r._TP_ac(r.cargo_throughput), C.TPC_ADJCOST, cache=False, result=float)
	TPp_adjcost = generated(lambda r: r._TP_ac(r.profit_throughput), C.TPP_ADJCOST, cache=False, result=float)
	TPc_cash = generated(lambda r: r._TPc(C.CASH), C.TPC_CASH, tbl="TPc/Money", result=float)
	TPp_cash = generated(lambda r: r._TPp(C.CASH), C.TPP_CASH, tbl="TPp/Money", result=float)
	TPc_coal = generated(lambda r: r._TPc(C.COAL), C.TPC_COAL, result=float)
	TPp_coal = generated(lambda r: r._TPp(C.COAL), C.TPP_COAL, result=float)
	TPc_diesel = generated(lambda r: r._TPc(C.DIESEL), C.TPC_DIESEL, result=float)
	TPp_diesel = generated(lambda r: r._TPp(C.DIESEL), C.TPP_DIESEL, result=float)
	TPc_electric = generated(lambda r: r._TPc(C.ELECTRIC), C.TPC_ELECTRIC, result=float)
	TPp_electric = generated(lambda r: r._TPp(C.ELECTRIC), C.TPP_ELECTRIC, result=float)

	#   Wagon-specific
	def _compound(self, v: float) -> float:
		return (v/self.length)*(10*v/self.weight_full)
	compound_efficiency = generated(lambda r: r._compound(r.capacity), C.COMPOUND_EFFICIENCY, result=float)
	compound_profitability = generated(lambda r: r._compound(r.profit), C.COMPOUND_PROFITABILITY, result=float)
	density = generated(lambda r: r.weight_full/r.length, C.DENSITY, result=float, disp=Disp.Negative)
	wt_per_cargo = generated(lambda r: safe_div(r.weight_full, r.capacity), C.WT_PER_CARGO, result=float, disp=Disp.Negative)
	@generated(C.CARGO_UNIT_WT, result=float, disp=Disp.Negative)
	def cargo_unit_wt(self):
		return safe_div(self.weight_full-self.weight_empty, self.capacity)

	def is_engine(self):
		return self.vehicle_type == 0 and self.cost
	def is_wagon(self):
		return self.vehicle_type == 0 and self.ctype
	def is_vehicle(self):
		return self.vehicle_type == 1
	def is_aircraft(self):
		return self.vehicle_type == 3

@finalize
class tcoords:
	source = field(Path, 'source', C.SOURCE, default='')
	id = xml_field(str, 'id')
	x = xml_field(int, 'x')
	y = xml_field(int, 'y')
	w = xml_field(int, 'w')
	h = xml_field(int, 'h')

def compare(row1, row2, fields):
	for f in fields:
		if row1[f] < row2[f]:
			return True
		elif row2[f] < row1[f]:
			return False
	return False

time_speed = 0.33
tick_rate = 0.1
token_supply = {
	C.CASH: 1000.0, C.COAL: 500.0, C.DIESEL: 250.0, C.ELECTRIC: 0.0
}

fuel_per_year = (tick_rate*365/time_speed)/5.0

adj_scale = 1000
fixed_scale = {C.CASH: 1000, C.COAL: 1000, C.DIESEL: 1000, C.ELECTRIC: 1000}
token_by_label = {
	"F1283C03": C.COAL, "F29BF6C1": C.DIESEL,
	"F9D8BF64": C.ELECTRIC}
cargo_by_label = {
	"0BA458C8": "Passenger",	"0F822763": "Mail",  	"3199AA74": "Logs",
	"448DDF23": "Lumber",   	"6ACBCBA9": "Coal",  	"61A13BCE": "Ore",
	"7C13D1C9": "Iron",     	"19CFBDA7": "Oil",   	"53F1B093": "Diesel",
	"B388ED8C": "Goods",    	"94032E35": "Sand",  	"88D1A491": "Steel",
	"C74198A7": "Food",     	"762F8F3E": "Limestone","8DFA75B5": "Cement",
	"9A988702": "Garbage"
}


def rnd(x: T, recip_tol=0) -> T:
	try:
		if type(x) is not bool and recip_tol == 0 and int(x) == x:
			return int(x)
	except:
		pass
	recip_tol = recip_tol or 100
	return math.floor(x*recip_tol)/recip_tol if type(x) is float else x

def costs(raw: str) -> dict[str, float]:
	raw = re.findall(r'-([0-9.]+)(?:\[([^[]+)\])?;?', raw)
	return {token_by_label.get(t, C.CASH): float(x) for x, t in raw}

def adj_costs(cost: dict[str, float]) -> list[float]:
	cost_adj_d = {
		t: fuel_per_year/x if x != 0 else 2
		for t, x in token_supply.items()
	}
	return [cost.get(t,0)*x/cost_adj_d[C.CASH] for t, x in cost_adj_d.items()]

def cost_adj(cost: dict[str, float]) -> float:
	return sum(adj_costs(cost))

def parse_eras(raw_epoch: str) -> str:
	t_eras = [0]*8
	epochs = re.findall(r'([0-9]+)(?:-([0-9]+))?,?+', raw_epoch)
	for r in epochs:
		for e in range(int(r[0]), int(r[1] if r[1] else r[0])+1):
			if e < len(t_eras):
				t_eras[e] = e
	return "".join([str(e) for e in t_eras if e]) or '0'

all_labels = Row.keys()
currencies = ['cash', 'coal', 'diesel', 'electric',]
train_direct_labels = [
	'name', 'max_speed', 'traction', 'power', 'weight', 'length', 'era'
]

train_row_labels = [
	'name', 'max_speed', 'traction', 'power', 'weight', 'length', 'era',
	'towage', 'pwt_empty', 'pwt_full', 'tow_per_length', 'power_per_length',
	'throughput', 'CD6', 'CD8', 'max_speed_mph',
	'TP_cash', 'TP_coal', 'TP_diesel', 'TP_electric',
	]+currencies+[
	'TP_adjcost', 'adjcost', # C.COSTS_RAW,
	'eras', 'id', 'source'
]

wagon_direct_labels = [
	'name', 'ctype', 'capacity', 'weight_empty', 'weight_full', 'length', 'era',
	'bonus'
]

wagon_row_labels = [
	'name', 'ctype', 'capacity', 'weight_empty', 'weight_full', 'length', 'era',
	'bonus', 'cargo_per_length', 'cargo_per_wt', 'compound_efficiency',
	'density', 'profit', 'profit_per_length', 'profit_per_wt',
	'compound_profitability', 'wt_per_cargo', 'cargo_unit_wt',
	'eras', 'id', 'cid', 'source',
	'power'
]

acurrencies = ['adjcost'] + currencies
map_curs = lambda pfx: [pfx + cur for cur in acurrencies]
vehicle_row_labels = [
	'name', 'ctype', 'capacity', 'max_speed', 'power', 'weight_empty',
	'weight_full', 'length', 'era', 'bonus', 'pwt_empty', 'pwt_full',
	'throughput', 'cargo_throughput', 'cargo_per_length', 'profit',
	'profit_per_length', 'cargo_unit_wt', 'max_speed_mph',
	]+currencies+[ 'adjcost',
	]+map_curs('TP_')+currencies+map_curs('TPc_')+map_curs('TPp_')+[
	# C.COSTS_RAW,
	'eras', 'id', 'cid', 'source'
]

labels_by_type = {
	"engine": train_row_labels,
	"wagon": wagon_row_labels,
	"vehicle": vehicle_row_labels,
	"aircraft": vehicle_row_labels,
	"all": all_labels
}

# QSQLITE_ENABLE_REGEXP
class TableModel(QAbstractTableModel):
	data: list[Row]
	def __init__(self):
		super().__init__()
		pass

class Proxy(QSortFilterProxyModel):
	pass
