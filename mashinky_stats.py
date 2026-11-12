from pathlib import Path
import argparse
import csv
import math
import re
import sys
import warnings
import types
import typing
from typing import Any, Generic, Optional, Type, TypeVar
from dataclasses import dataclass
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import constants as C

def slurp(filename):
	try:
		with open(filename, "r", encoding="utf-8") as f:
			return f.read()
	except UnicodeError:
		with open(filename, "r", encoding="utf-16") as f:
			return f.read()

class _default:
	def __bool__(self):
		return False
Default = _default()
_default.__new__ = lambda self, *args: Default
_default.__call__ = lambda self, *args: Default
otherwise = lambda a, b: a if a is not Default else b
T = TypeVar('T')
safe_div = lambda a, b: a/b if b else 0.
class FieldBase:
	csv: Optional[str]
	tbl: Optional[str]
	owner: None
	def _key(self):
		return f"key-{self._key_name}"
class KeyBase(FieldBase):
	xml: Optional[str]
	_key_name: str

def field(U: Type, csv: Optional[str], tbl: Optional[str] = Default, /,
	xml : Optional[str] = None, default: Optional[T] = Default):
	"""def field(U: Type, csv: Optional[str], tbl: Optional[str] = csv, /,
		xml : Optional[str] = None, default : Optional[T] = Default):
	If only csv is specified, tbl reuses that value. If default is specified,
	the field has that as its default value, otherwise there is no default."""
	# name lookup gets confused by the class shadowing the closure-captured args
	csv_ = csv
	tbl_ = otherwise(tbl, csv_)
	xml_ = xml

	class Key(KeyBase):
		owner = None
		def __init__(self):
			object.__setattr__(self,'csv', csv_)
			object.__setattr__(self,'tbl', tbl_)
			object.__setattr__(self,'xml', xml_)
			object.__setattr__(self,'_key_name', csv_)
		def __set_name__(self, owner, name):
			if not isinstance(owner, type):
				object.__setattr__(self, 'owner', owner)
			object.__setattr__(self, '_key_name', name)
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
def default_field(*args, xml=None):
	return field(*args, xml=xml, default=None)
def zero_field(*args, xml=None):
	return field(*args, xml=xml, default=0)
def table_field(U: T, tbl: str, /, xml : Optional[str] = None,
	default: Optional[T] = Default):
	"""For fields which are not in the CSV but are in the table"""
	return field(U, None, tbl, xml=xml, default=default)
def xml_field(U: T, xml : Optional[str] = None, /, tbl: str = Default,
	default: Optional[T] = Default):
	"""Non-CSV fields"""
	return field(U, None, tbl, xml=xml, default=default)
def zero_xml_field(U: T, xml : Optional[str] = None, /, tbl: str = Default):
	return field(U, None, tbl, xml=xml, default=0)
def default_xml_field(U: T, xml : Optional[str] = None, /, tbl: str = Default):
	return field(U, None, tbl, xml=xml, default=None)

def generated(first, *args, **kwargs):
	"""Generates a field from others. Cannot have an xml key.
	generated(fun: types.FunctionType, csv_: str, tbl_: Optional[str] = Default):
		Value of obj.gen is computed as fun(obj). tbl defaults to csv
	@generated(csv_: str, tbl_: Optional[str] = Default):
		decorator version of the above"""
	def impl(fun: types.FunctionType, csv_: Optional[str], tbl_: Optional[str] = Default, cache=True):
		class Gen(FieldBase):
			owner = None
			def __init__(self):
				object.__setattr__(self,'csv', csv_)
				object.__setattr__(self,'tbl', otherwise(tbl_, csv_))
			def __set_name__(self, owner, name):
				if not isinstance(owner, type):
					object.__setattr__(self, 'owner', owner)
				object.__setattr__(self, '_key_name', name)
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
	if type(first) == str:
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
	index = table_field(int, 'Index')
	source = field(Path, 'source', C.SOURCE, default='')
	vanilla = table_field(bool, C.VANILLA, default=False)
	id = field(str, 'id', 'ID', xml=C.ID, default='')
	cid = default_field(Optional[str], C.CID, 'Cargo ID', xml='cargo')
	vehicle_type = table_field(int, 'vehicle_type', xml='vehicle_type')
	track = zero_field(int, None, C.TRACK, xml='track')
	weight_full = field(float, C.WEIGHT_FULL, xml='weight_full')
	weight_empty = field(float, C.WEIGHT_EMPTY, xml='weight_empty')
	epoch = field(str, C.EPOCHS, xml='epoch', default='')
	eras = generated(lambda r: parse_eras(r.epoch), C.ERAS)
	era = generated(lambda r: r.eras[0], C.ERA)

	icon = xml_field(str, 'icon', default="")
	icon_texture = xml_field(str, 'icon_texture', default="")
	icon_color = xml_field(str, 'icon_color', default="")

	length_b = zero_xml_field(float, 'length')
	length_head = zero_xml_field(float, 'head_length')
	length_tail = zero_xml_field(float, 'tail_length')
	length = generated(lambda r: r.length_b + r.length_head + r.length_tail, C.LENGTH)

	#   Prime movers:
	power = field(float, C.POWER, xml='power', default=0.)
	max_speed = field(float, C.SPEED, xml='max_speed', default=0.)
	max_speed_mph = generated(lambda r: r.max_speed/C.KM_PER_MI, C.SPEED_MPH)
	max_speed_reverse = zero_field(Any, None, "Reverse speed (km/hr)", xml='max_speed_reverse')
	@generated("Reverse speed (mph)")
	def max_speed_reverse_mph(self):
		if type(self.max_speed_reverse) is float:
			return round(self.max_speed_reverse/C.KM_PER_MI)
		else:
			return self.max_speed_reverse
	weight = generated(lambda r: r.weight_full, C.WEIGHT)
	@generated(C.TRACTION)
	def traction(self):
		return math.floor(safe_div(self.power*C.TRACTION_SCALE, self.max_speed))
	towage = generated(lambda r: r.traction - r.weight_full, C.TOWAGE)
	throughput = generated(lambda r: r.towage*r.max_speed, C.THROUGHPUT)

	# Fuel
	raw_cost = table_field(str, None, xml='fuel_cost', default='')
	cost = generated(lambda r: costs(r.raw_cost), C.COSTS_RAW)
	cash = generated(lambda r: r.cost.get(C.CASH, 0.), C.CASH)
	coal = generated(lambda r: r.cost.get(C.COAL, 0.), C.COAL)
	diesel = generated(lambda r: r.cost.get(C.DIESEL, 0.), C.DIESEL)
	electric = generated(lambda r: r.cost.get(C.ELECTRIC, 0.), C.ELECTRIC)
	adjcost = generated(lambda r: cost_adj(r.cost), C.ADJCOST, cache=False)

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
			return float(effect.group(1))-1
		else:
			return 1
	@generated(C.BONUS)
	def bonus(self):
		effect = re.fullmatch(r'(?:profit\[[^]]*\])\*([0-9]*.?[0-9]*)',
			self.raw_effect)
		if effect:
			return round(100*(float(effect.group(1))-1))
		else:
			return ''

	# Ratios and composites:
	#   Prime movers:
	pwt_full = generated(lambda r: safe_div(r.power, r.traction), C.PWT_FULL)
	pwt_empty = generated(lambda r: r.power/r.weight_full, C.PWT_EMPTY)
	tow_per_length = generated(lambda r: r.towage/r.length, C.TOW_PER_LENGTH)
	power_per_length = generated(lambda r: r.power/r.length, C.POWER_PER_LENGTH)

	#   Cargo carriers:
	profit = generated(lambda r: r.capacity*r.effect, C.PROFITABILITY)
	cargo_per_length = generated(lambda r: r.capacity/r.length, C.CARGO_PER_LENGTH)
	profit_per_length = generated(lambda r: r.profit/r.length, C.PROFIT_PER_LENGTH)
	cargo_per_wt = generated(lambda r: 10*r.capacity/r.weight_full, C.CARGO_PER_WT)
	profit_per_wt = generated(lambda r: 10*r.profit/r.weight_full, C.PROFIT_PER_WT)

	#   Units: (i.e. power and capacity both != 0)
	cargo_throughput = generated(lambda r: r.capacity*r.max_speed, C.TP_CARGO)
	profit_throughput = generated(lambda r: r.profit*r.max_speed, C.TP_PROFIT)

	#   Fuel:
	def _TP(self, c: str, t: float) -> float:
		if self.power and self.cost.get(c):
			return t/(self.cost.get(c, 0)*fixed_scale[c])
		else:
			return ''
	def TP_ac(self, t: float) -> float:
		return self.adjcost and t/(self.adjcost*adj_scale)
	def TP(self, cur: str) -> float:
		return self._TP(cur, self.throughput)
	def TPc(self, cur: str) -> float:
		return self._TP(cur, self.cargo_throughput)
	def TPp(self, cur: str) -> float:
		return self._TP(cur, self.profit_throughput)

	TP_adjcost = generated(lambda r: r.TP_ac(r.throughput), C.TP_ADJCOST, cache=False)
	TP_cash = generated(lambda r: r.TP(C.CASH), C.TP_CASH)
	TP_coal = generated(lambda r: r.TP(C.COAL), C.TP_COAL)
	TP_diesel = generated(lambda r: r.TP(C.DIESEL), C.TP_DIESEL)
	TP_electric = generated(lambda r: r.TP(C.ELECTRIC), C.TP_ELECTRIC)

	TPc_adjcost = generated(lambda r: r.TP_ac(r.cargo_throughput), C.TPC_ADJCOST, cache=False)
	TPp_adjcost = generated(lambda r: r.TP_ac(r.profit_throughput), C.TPP_ADJCOST, cache=False)
	TPc_cash = generated(lambda r: r.TPc(C.CASH), C.TPC_CASH)
	TPp_cash = generated(lambda r: r.TPp(C.CASH), C.TPP_CASH)
	TPc_coal = generated(lambda r: r.TPc(C.COAL), C.TPC_COAL)
	TPp_coal = generated(lambda r: r.TPp(C.COAL), C.TPP_COAL)
	TPc_diesel = generated(lambda r: r.TPc(C.DIESEL), C.TPC_DIESEL)
	TPp_diesel = generated(lambda r: r.TPp(C.DIESEL), C.TPP_DIESEL)
	TPc_electric = generated(lambda r: r.TPc(C.ELECTRIC), C.TPC_ELECTRIC)
	TPp_electric = generated(lambda r: r.TPp(C.ELECTRIC), C.TPP_ELECTRIC)

	#   train-specific
	CD6 = generated(lambda r: r.towage/(6-r.length), C.CD6)
	CD8 = generated(lambda r: r.towage/(8-r.length), C.CD8)

	#   wagon-specific
	def _compound(self, v: float) -> float:
		return (v/self.length)*(10*v/self.weight_full)
	compound_efficiency = generated(lambda r: r._compound(r.capacity), C.COMPOUND_EFFICIENCY)
	compound_profitability = generated(lambda r: r._compound(r.profit), C.COMPOUND_PROFITABILITY)
	density = generated(lambda r: r.weight_full/r.length, C.DENSITY)
	wt_per_cargo = generated(lambda r: safe_div(r.weight_full, r.capacity), C.WT_PER_CARGO)
	@generated(C.CARGO_UNIT_WT)
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


def rnd(x: T, recip_tol=100) -> T:
	try:
		if type(x) is not bool and int(x) == x:
			return int(x)
	except:
		pass
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

def read_expected(filename):
	ret = {}
	if filename:
		with open(filename, "r", newline='') as file:
			reader = csv.DictReader(file, quoting=csv.QUOTE_NONNUMERIC)
			for row in reader:
				try:
					#val = Row.from_csv(row)
					#print(f"read_expected: {row} -> {val}")
					val = {
						f: (None if type(v) is str and v.startswith('#') else v) for f, v in row.items()
							if not (type(v) is str and v.startswith('='))
					}
					try:
						if type(val[C.ERA]) is float:
							val[C.ERA] = str(int(val[C.ERA]))
						val[C.ERAS] = parse_eras(val[C.ERA])
					except KeyError as e:
						e.add_note(repr(val))
						raise
					ret[exp_name_key(val[C.NAME])] = {
						'data': val,
						'seen': False
					}
				except KeyError as e:
					e.add_note(f"in: {repr(val)}, source: {filename}")
					raise
	return ret

def compare_exp_val(val, exp, field):
	if type(exp) is str or type(val) is str:
		return val == exp
	elif type(exp) is float or type(exp) is int:
		if ('/' in field or field in [C.DENSITY, C.COMPOUND_EFFICIENCY, C.COMPOUND_PROFITABILITY]) and exp != 0:
			return .95 < val/exp < 1.05
		else:
			return abs(val-exp) <= .01
	elif (val == 0 or val == '') and exp is None:
		return True
	else:
		return val == exp

def key_to_csv(field):
	return Row.__dict__[field].csv
def keys_to_csv(fields):
	return [key_to_csv(field) for field in fields]
def exp_name_key(name):
	return re.fullmatch(r'\W*(.*?)\W*', name.lower()).group(1)

def compare_vehicle(vehicle, expected, label, fields, elementary_fields, fmt, out):
	if expected is None:
		print(
			f"{label} new: {fmt(vehicle)} ID={vehicle.id}:{vehicle.source}",
			file=out)
	elif vehicle is None:
		if not '*' in expected[C.NAME]:
			print(f"{label} missing: {fmt(expected)}", file=out)
	else:
		discrepancy = []
		for field in fields:
			try:
				if key_to_csv(field) in expected \
					and not compare_exp_val(vehicle.get(field), expected[key_to_csv(field)],
					field):
					discrepancy.append(field)
			except AttributeError as e:
				e.add_note(f"expected: {repr(expected)}")
				e.add_note(f"{field}: {repr(vehicle.get(field))} {repr(expected.get(key_to_csv(field)))}")
				e.add_note(repr(vehicle) + " " + repr(expected))
				raise
		if discrepancy:
			print(
				f"{label} diff: got ({fmt(vehicle)}) expected ({fmt(expected)}) "
				f"ID={vehicle.id}:{vehicle.source}",
				file=out)
			print("\t" + "; ".join(
				["{}{}:{},{}".format("!" if f in elementary_fields else "=",
					f, repr(rnd(vehicle[f])), repr(rnd(expected[key_to_csv(f)])))
					for f in discrepancy]),
				file=out)

ign_fields = ['name', 'era', 'eras', 'max_speed_mph']
def elem(fields):
	return list(filter(lambda x: x not in ign_fields and 'adjcost' not in x, fields))

def compare_train(vehicle, expected, out):
	def fmt(t):
		if isinstance(t, Row):
			return "{n} ({e}) s={s} p={p} w={w} l={l} c={c}".format(
				n=t.name, e=t.get('eras', t.era),
				s=rnd(t.max_speed),
				p=rnd(t.power), w=rnd(t.weight_full),
				l=rnd(t.length),
				c=f"{rnd(t.cash)};{rnd(t.coal)}c;{rnd(t.diesel)}d;{rnd(t.electric)}e")
		else:
			try:
				return "{n} ({e}) s={s} p={p} w={w} l={l} c={c}".format(
					n=t[C.NAME], e=t.get(C.ERAS, t[C.ERA]),
					s=rnd(t[C.SPEED]),
					p=rnd(t[C.POWER]), w=rnd(t[C.WEIGHT]),
					l=rnd(t[C.LENGTH]),
					c=f"{rnd(t[C.CASH])};{rnd(t[C.COAL])}c;{rnd(t[C.DIESEL])}d;{rnd(t[C.ELECTRIC])}e")
			except KeyError as e:
				e.add_note(repr(t))
				raise
	return compare_vehicle(vehicle, expected, 'train', elem(train_row_labels), train_direct_labels, fmt, out)

def compare_wagon(vehicle, expected, out):
	def fmt(t):
		if isinstance(t, Row):
			return "{n} ({e}) t={t} c={c} wu={wu} wl={wl} l={l} b={b} p={p}".format(
				n=t.name, e=t.get('eras', t.era),
				t=rnd(t.ctype), c=rnd(t.capacity),
				wu=rnd(t.weight_empty), wl=rnd(t.weight_full),
				l=rnd(t.length), b=rnd(t.bonus), p=rnd(t.power))
		else:
			return "{n} ({e}) t={t} c={c} wu={wu} wl={wl} l={l} b={b} p={p}".format(
				n=t[C.NAME], e=t.get(C.ERAS, t[C.ERA]),
				t=rnd(t[C.TYPE]), c=rnd(t[C.CARGO]),
				wu=rnd(t[C.WEIGHT_EMPTY]), wl=rnd(t[C.WEIGHT_FULL]),
				l=rnd(t[C.LENGTH]), b=rnd(t[C.BONUS]), p=rnd(t.get(C.POWER)))
	return compare_vehicle(vehicle, expected, 'wagon', elem(wagon_row_labels), wagon_direct_labels, fmt, out)

def read_files(files, vfiles):
	idx = 0
	coords = {}
	def impl(files, vanilla):
		nonlocal idx
		out = []
		try:
			for file in files:
				dom = BeautifulSoup(slurp(file), "lxml")
				for tag in dom.find_all('wagontype'):
					out.append(Row.from_xml(tag.attrs, source=file, vanilla=vanilla, index=idx))
					#print(out[-1].asdict(False))
					idx = idx + 1
				for tag in dom.find_all('coord'):
					#print(f"{repr(tag.attrs)}, source={file}")
					nonlocal coords
					coord = tcoords.from_xml(tag.attrs, source=file)
					coords |= {coord.id: coord}
		except ValueError as e:
			e.add_note(repr(tag.attrs))
			e.add_note(repr(file))
			raise
		return out
	return impl(vfiles, True)+impl(files, False), coords

def process_files(table, out, msg, fields, pred, exp, comp, exp_out):
	def impl(outfile, table):
		writer = csv.DictWriter(
			outfile, fieldnames=keys_to_csv(fields),
			quoting=csv.QUOTE_NONNUMERIC, extrasaction='ignore')
		writer.writeheader()
		for vehicle in (row for row in table if pred(row)):
			writer.writerow(vehicle.to_csv())
			if exp:
				try:
					name = exp_name_key(vehicle.name)
					e = exp.get(name)
					comp(vehicle, e['data'] if e else None, exp_out)
					if e:
						e['seen'] = True
				except KeyError as e:
					e.add_note(repr(vehicle))
					e.add_note(f"in {vehicle['id']}, source: {vehicle['source']}")
					raise
		if exp:
			for vehicle in (
				vehicle['data'] for vehicle in exp.values()
				if not vehicle['seen']
			):
				comp(None, vehicle, exp_out)
	if out == '-':
		print(msg)
		impl(sys.stdout, table)
	else:
		with open(out, 'w', newline='') as outfile:
			impl(outfile, table)

def run(files, vfiles, train_out, wagon_out, vehicle_out, aircraft_out, univ_out, expected_trains, expected_wagons, unexpected_outstream):
	table, coords = read_files(files, vfiles)
	print(repr(coords))

	process_files(table, train_out, "Trains:", train_row_labels,
		Row.is_engine,
		expected_trains, compare_train, unexpected_outstream)

	process_files(table, wagon_out,"Wagons:", wagon_row_labels,
		Row.is_wagon,
		expected_wagons, compare_wagon, unexpected_outstream)

	process_files(table, vehicle_out, "Vehicles:", vehicle_row_labels,
		Row.is_vehicle,
		None, None, None)

	process_files(table, aircraft_out, "Aircraft:", vehicle_row_labels,
		Row.is_aircraft,
		None, None, None)

	if univ_out:
		process_files(table, univ_out, "All:", all_labels,
			lambda a: True,
			None, None, None)

def make_arg_parser(gui):
	parser = argparse.ArgumentParser()
	parser.add_argument('files', nargs='*',
		help='Paths to individual xml files to parse')
	parser.add_argument('-p', '--path', action='append', default=[],
		help='Path(s) to mods root directory')
	parser.add_argument('-V', '--vanilla', action='append', default=[],
		help="Path(s) to individual files for vanilla trains")
	parser.add_argument('-P', '--vanilla_dir', action='append', default=[],
		help="Path(s) to directories of files for vanilla trains")
	parser.add_argument('-I', '--vanilla_media',
		help="Path to vanilla media folder")
	parser.add_argument('-T', '--expected_trains')
	parser.add_argument('-W', '--expected_wagons')
	parser.add_argument('-i', '--income')
	if gui:
		parser.add_argument('-c', '--cmap', action='append', default=[])
	else:
		parser.add_argument('-t', '--train_out', default='-')
		parser.add_argument('-w', '--wagon_out', default='-')
		parser.add_argument('-r', '--vehicle_out', default='-')
		parser.add_argument('-a', '--aircraft_out', default='-')
		parser.add_argument('-u', '--univ_out')
		parser.add_argument('-d', '--unexpected_out', default='-')
	return parser

def find_files(files, paths):
	files = [Path(f) for f in files]
	for file in files:
		if not file.exists() or not file.is_file():
			raise IOError('Invalid file ' + str(file))

	for raw_path in paths:
		path = Path(raw_path)
		if not path.exists or not path.is_dir():
			raise IOError('Invalid path ' + str(path))
		for file in path.glob('*/config/wagon_types.xml'):
			files.append(file)
		for file in path.glob('*/config/tcoords.xml'):
			files.append(file)
	return files

def read_incomes(income):
	parsed = re.fullmatch(
		r'(\d+)[;, ](\d+)c[;, ](\d+)d[;, ](\d+)e', income)
	if parsed:
		token_supply[C.CASH] = int(parsed.group(1))
		token_supply[C.COAL] = int(parsed.group(2))
		token_supply[C.DIESEL] = int(parsed.group(3))
		token_supply[C.ELECTRIC] = int(parsed.group(4))
	else:
		raise ValueError("Could not parse --income argument: "
			+ repr(income))

def handle_cli(gui):
	warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
	parser = make_arg_parser(gui)
	args = parser.parse_args()
	files = find_files(args.files, args.path)
	vfiles = find_files(args.vanilla, args.vanilla_dir)

	if args.income:
		read_incomes(args.income)

	return args, files, vfiles

def main():
	args, files, vfiles = handle_cli(False)
	with (sys.stdout
	      if args.unexpected_out == '-'
			else open(args.unexpected_out, 'w', newline='')
	as unexpected_outstream):
		expected_trains = read_expected(args.expected_trains)
		expected_wagons = read_expected(args.expected_wagons)
		
		run(files, vfiles, args.train_out, args.wagon_out, args.vehicle_out, args.aircraft_out, args.univ_out, expected_trains, expected_wagons, unexpected_outstream)
	
if __name__ == '__main__':
	main()
