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
				#print(f"setting default={repr(default)}, csv={csv_}, tbl={tbl_}")
				object.__setattr__(self, 'default', default)
			owner.__annotations__[name] = U
		def _key(self):
			return f"key-{self._key_name}"
		def __get__(self, obj, owner=None):
			def fmt_key(k):
				if k.is_default():
					return f"Key({self._key_name}, {repr(k.csv)}, {repr(k.tbl)}, xml={repr(k.xml)}, default={repr(k.default)}, owner={repr(k.owner)})"
				else:
					return f"Key({self._key_name}, {repr(k.csv)}, {repr(k.tbl)}, xml={repr(k.xml)}, owner={repr(k.owner)})"
			#print(fmt_key(self), f"<class {repr(type(obj).__name__)}>", repr(owner), sep=';')
			if obj is not None:
				try:
					if self._key() in obj.__dict__:
						return obj.__dict__[self._key()]
					elif self.is_default(obj):
						if type(self.default) is U or type(self.default) in typing.get_args(U):
							return self.default
						else:
							return U(self.default)
					else:
						raise AttributeError(f"'{owner.__name__}' field '{self._key_name}' unset")
				except KeyError as e:
					raise AttributeError(f"'{owner.__name__}' field '{self._key_name}' unset") from e
			else:
				return self
		def is_default(self, *args):
			if not args:
				return hasattr(self, 'default')
			else:
				return self._key() not in args[0].__dict__ and hasattr(self, 'default')
		def __repr__(self):
			if self.owner:
				try:
					value = self.__get__(self.owner, type(self.owner))
					return f"<Key {self._key_name}={repr(value)}>"
				except AttributeError:
					return f"<Key {self._key_name}=unset>"
			else:
				return (f"<Key '{self._key_name}'('{self.csv}', '{self.tbl}', xml='{self.xml}'"
					+ (f", default={default})>" if default is not Default else ")>"))
		def __set__(self, obj, value):
			#print(repr(self), repr(obj), repr(value), sep=';')
			obj.__dict__[self._key()] = value
		def __setattr__(self, name, value):
			raise AttributeError(f"Key.{name}={value}: Keys are immutable")
		def __delattr__(self, name):
			raise AttributeError(f"del Key.{name}: Keys are immutable")
	k = Key()
	return k
def default_field(*args, xml=None):
	return field(*args, xml=xml, default=None)
def zero_field(*args, xml=None):
	return field(*args, xml=xml, default=0)
def table_field(U: T, tbl: str, /, xml : Optional[str] = None,
	default: Optional[T] = Default):
	"""For fields which are not in the CSV but are in the table"""
	return field(U, None, tbl, xml=xml, default=default)

def generated(first, *args, **kwargs):
	"""Generates a field from others. Cannot have an xml key.
	generated(fun: types.FunctionType, csv_: str, tbl_: Optional[str] = Default):
		Value of obj.gen is computed as fun(obj). tbl defaults to csv
	@generated(csv_: str, tbl_: Optional[str] = Default):
		decorator version of the above"""
	def impl(fun: types.FunctionType, csv_: Optional[str], tbl_: Optional[str] = Default):
		class Key(FieldBase):
			def __init__(self):
				object.__setattr__(self,'csv', csv_)
				object.__setattr__(self,'tbl', otherwise(tbl_, csv_))
				def __set_name__(self, owner, name):
					if not isinstance(owner, type):
						object.__setattr__(self, 'owner', owner)
					object.__setattr__(self, '_key_name', name)
			def __get__(self, obj, owner=None):
				#print(repr(self), repr(obj), repr(owner), sep=';')
				if obj is not None:
					return fun(obj)
				else:
					return self
			def is_default(self, *args):
				return True
			def __repr__(self):
				if self.owner:
					try:
						value = self.__get__(self.owner, type(self.owner))
						return f"<Key {self._key_name}={repr(value)}>"
					except AttributeError:
						return f"<Key {self._key_name}=unset>"
				else:
					return f"<Key '{self._key_name}'('{self.csv}', '{self.tbl}')>"
			def __set__(self, obj, value):
				raise AttributeError(f"{obj}.key-{self.csv}={value}: Generated fields cannot be assigned")
			def __setattr__(self, name, value):
				raise AttributeError(f"Key.{name}={value}: Keys are immutable")
			def __delattr__(self, name):
				raise AttributeError(f"del Key.{name}: Keys are immutable")
		return Key()
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
		rep = ", ".join((f"{k[0]}={self.field_rep(k[0])}" for k in dict(vars(cls)).items()
			if isinstance(k[1], KeyBase) and k[0] in self))
		return f"{type(self).__name__}({rep})"
	cls.__repr__ = rep
	#def field_str(self, field):

	init_fields = {}
	out_fields = {}
	for k,v in dict(vars(cls)).items():
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
					self.__setattr__(k, v)
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
		fields = self.assign_args(strict=strict, **kwargs)
		if fields:
			raise ValueError(f"{cls.__name__}.from_args(): "\
				f"missing required keyword arguments {list(fields.keys())}")
	def from_args(cls, /, strict=False, **kwargs):
		r = cls()
		init(r)
		return r
	cls.from_args = classmethod(from_args)
	if '__init__' not in vars(cls):
		cls.__init__ = init
	def from_(attr, fields_):
		def impl(cls, obj_, /, strict=False, **kwargs):
			fields = fields_.copy()
			obj = obj_.copy()
			r = cls()
			for k,v in obj.copy().items():
				for f,ks in fields.items():
					if ks[attr] == k:
						r.__setattr__(f,v)
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
					if not hasattr(v, 'default') and k in f2:
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
	index = table_field(int, 'index')
	source = table_field(Path, C.SOURCE, default='')
	vanilla = table_field(bool, C.VANILLA, default=False)
	id = table_field(str, C.ID, xml=C.ID, default='')
	cid = default_field(Optional[str], C.CID, xml='cargo')
	name = field(str, C.NAME, xml='name')
	vehicle_type = table_field(int, 'vehicle_type', xml='vehicle_type')
	track = zero_field(int, None, C.TRACK, xml='track')
	weight_full = field(float, C.WEIGHT_FULL, xml='weight_full')
	weight_empty = field(float, C.WEIGHT_EMPTY, xml='weight_empty')
	epoch = field(str, C.EPOCHS, xml='epoch', default='')
	eras = generated(lambda r: parse_eras(r.epoch), C.ERAS)
	era = generated(lambda r: r.eras[0], C.ERA)

	icon = table_field(str, "Icon", xml='icon', default="")

	length_b = zero_field(float, None, xml='length')
	length_head = zero_field(float, None, xml='head_length')
	length_tail = zero_field(float, None, xml='tail_length')
	length = generated(lambda r: r.length_b + r.length_head + r.length_tail, C.LENGTH)

	cost = table_field(dict[str, float], C.COSTS_RAW, xml='fuel_cost', default={})
	cash = generated(lambda r: r.cost.get(C.CASH, 0.), C.CASH)
	coal = generated(lambda r: r.cost.get(C.COAL, 0.), C.COAL)
	diesel = generated(lambda r: r.cost.get(C.DIESEL, 0.), C.DIESEL)
	electric = generated(lambda r: r.cost.get(C.ELECTRIC, 0.), C.ELECTRIC)

	#   Prime movers:
	power = field(float, C.POWER, xml='power', default=0.)
	max_speed = field(float, C.SPEED, xml='max_speed', default=0.)
	max_speed_reverse = zero_field(float, None, "Reverse speed (km/hr)", xml='max_speed_reverse')
	max_speed_mph = generated(lambda r: round(r.max_speed/C.KM_PER_MI), C.SPEED_MPH)
	max_speed_reverse_mph = generated(lambda r: round(r.max_speed_reverse/C.KM_PER_MI), "Reverse speed (mph)")
	weight = generated(lambda r: r.weight_full, C.WEIGHT)
	@generated(C.TRACTION)
	def traction(self):
		return math.floor(safe_div(self.power*C.TRACTION_SCALE, self.max_speed))
	towage = generated(lambda r: r.traction - r.weight_full, C.TOWAGE)
	throughput = generated(lambda r: r.towage*r.max_speed, C.THROUGHPUT)

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
	raw_effect = field(str, None, xml='effect', default="")
	@generated(C.BONUS)
	def bonus(self):
		effect = re.fullmatch(r'(?:profit\[[^]]*\])\*([0-9]*.?[0-9]*)',
			self.raw_effect)
		if effect:
			return float(effect.group(1))
		else:
			return 1

	# Ratios and composites:
	#   Prime movers:
	pwt_full = generated(lambda r: safe_div(r.power, r.traction), C.PWT_FULL)
	pwt_empty = generated(lambda r: r.power/r.weight_full, C.PWT_EMPTY)
	tow_per_length = generated(lambda r: r.towage/r.length, C.TOW_PER_LENGTH)
	power_per_length = generated(lambda r: r.power/r.length, C.POWER_PER_LENGTH)

	#   Cargo carriers:
	profit = generated(lambda r: r.capacity*r.bonus, C.PROFITABILITY)
	cargo_per_length = generated(lambda r: r.capacity/r.length, C.CARGO_PER_LENGTH)
	profit_per_length = generated(lambda r: r.profit/r.length, C.PROFIT_PER_LENGTH)
	cargo_per_wt = generated(lambda r: 10*r.capacity/r.weight_full, C.CARGO_PER_WT)
	profit_per_wt = generated(lambda r: 10*r.profit/r.weight_full, C.PROFIT_PER_WT)

	#   Units: (i.e. power and capacity both != 0)
	cargo_throughput = generated(lambda r: r.capacity*r.max_speed, C.TP_CARGO)
	profit_throughput = generated(lambda r: r.profit*r.max_speed, C.TP_PROFIT)

	#   Fuel:
	adjcost = generated(lambda r: cost_adj(r.cost), C.ADJCOST)

	def _TP(self, c: str, t: float) -> float:
		if self.power and self.cost.get(c):
			return t/(self.cost.get(c, 0)*fixed_scale[c])
		else:
			return 0.
	def TP_ac(self, t: float) -> float:
		return self.adjcost and t/(self.adjcost*adj_scale)
	def TP(self, cur: str) -> float:
		return self._TP(cur, self.throughput)
	def TPc(self, cur: str) -> float:
		return self._TP(cur, self.cargo_throughput)
	def TPp(self, cur: str) -> float:
		return self._TP(cur, self.profit_throughput)

	tp_adjcost = generated(lambda r: r.TP_ac(r.throughput), C.TP_ADJCOST)
	tp_cash = generated(lambda r: r.TP(C.CASH), C.TP_CASH)
	tp_coal = generated(lambda r: r.TP(C.COAL), C.TP_COAL)
	tp_diesel = generated(lambda r: r.TP(C.DIESEL), C.TP_DIESEL)
	tp_electric = generated(lambda r: r.TP(C.ELECTRIC), C.TP_ELECTRIC)

	TPc_adjcost = generated(lambda r: r.TP_ac(r.cargo_throughput), C.TPC_ADJCOST)
	TPp_adjcost = generated(lambda r: r.TP_ac(r.profit_throughput), C.TPP_ADJCOST)
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
	return math.floor(x*recip_tol)/recip_tol if type(x) is float else x

def costs(train: dict[Any, Any]) -> dict[str, float]:
	raw = re.findall(r'-([0-9.]+)(?:\[([^[]+)\])?;?', train['fuel_cost'])
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

def all_stats(vehicle: dict[Any, Any], filename: Path = None, vanilla: bool = None):
	try:
		power = float(vehicle.get('power', 0))
		max_speed = float(vehicle.get('max_speed', 0))
		ctype = cargo_by_label.get(vehicle.get('cargo')) or ""
		if int(vehicle['vehicle_type']) == 0 and power and ctype == C.PASSENGER:
			ctype = "Pass. Engine"
		elif int(vehicle['vehicle_type']) == 0 and power and ctype == C.MAIL:
			ctype = "Mail Engine"
		capacity = float(vehicle.get('capacity', 0))
		weight_empty = float(vehicle['weight_empty'])
		weight_full = float(vehicle['weight_full'])
		
		if type(vehicle['epoch']) is float:
			vehicle['epoch'] = str(int(vehicle['epoch']))
		raw_epoch = vehicle['epoch']
		length = (
			float(vehicle.get('length', 0))
			+ float(vehicle.get('head_length', 0))
			+ float(vehicle.get('tail_length', 0))
		)
		
		cost = costs(vehicle) if vehicle.get('fuel_cost') else {}
		adjcost = cost_adj(cost)
		effect = re.fullmatch(r'(?:profit\[[^]]*\])\*([0-9]*.?[0-9]*)',
			vehicle.get('effect', ""))
		bonus = 1
		if effect:
			bonus = float(effect.group(1))
		profit = capacity*bonus
		
		traction = math.floor(C.TRACTION_SCALE*power/max_speed) if max_speed else 0
		towage = traction-weight_full
		throughput = towage*max_speed
		cargo_throughput = capacity*max_speed
		profit_throughput = profit*max_speed
		
		def TP_c(c, t):
			return (t/(cost.get(c, 0)*fixed_scale[c]) if power and cost.get(c)
				else 0.)
		TP = lambda c: TP_c(c, throughput)
		TPc = lambda c: TP_c(c, cargo_throughput)
		TPp = lambda c: TP_c(c, profit_throughput)
		
		eras = parse_eras(raw_epoch)
		#print(raw_epoch, repr(epochs), eras)
		
		return vehicle | {
			# technical info
			C.ID: str(vehicle[C.ID]),
			C.CID: str(vehicle.get('cargo', "")),
			C.SOURCE: str(filename) if filename is not None else vehicle[C.SOURCE],
			C.VANILLA: vanilla if vanilla is not None else vehicle.get(C.VANILLA, False),
			
			# common
			C.NAME: str(vehicle['name'].rstrip()),
			C.LENGTH: length,
			C.WEIGHT: weight_full,
			C.WEIGHT_FULL: weight_full,
			C.WEIGHT_EMPTY: weight_empty,
			C.EPOCHS: str(raw_epoch),
			C.ERA: int(eras[0]),
			C.ERAS: eras,
			C.TRACK: int(vehicle.get('track', 0)),
			
			# prime movers
			C.SPEED: max_speed,
			C.SPEED_MPH: round(max_speed/C.KM_PER_MI),
			C.POWER: power,
			C.TRACTION: traction,
			C.TOWAGE: towage,
			C.THROUGHPUT: throughput,
			C.PWT_FULL: safe_div(power, traction),
			C.PWT_EMPTY: power/weight_full,
			C.TOW_PER_LENGTH: towage/length,
			C.POWER_PER_LENGTH: power/length,
			
			# cargo carriers
			C.TYPE: ctype,
			C.CARGO: capacity,
			C.BONUS: round(100*(bonus-1)) if bonus != 1 else "",
			C.PROFITABILITY: profit,
			C.CARGO_PER_LENGTH: capacity/length,
			C.PROFIT_PER_LENGTH: profit/length,
			C.CARGO_PER_WT: 10*capacity/weight_full,
			C.PROFIT_PER_WT: 10*profit/weight_full,
			
			# units (i.e. power and capacity both != 0)
			C.TP_CARGO: cargo_throughput,
			C.TP_PROFIT: profit_throughput,
			
			# fuel
			C.ADJCOST: adjcost,
			C.CASH: cost.get(C.CASH, 0.),
			C.COAL: cost.get(C.COAL, 0.),
			C.DIESEL: cost.get(C.DIESEL, 0.),
			C.ELECTRIC: cost.get(C.ELECTRIC, 0.),
			
			C.TP_ADJCOST: adjcost and throughput/(adjcost*adj_scale),
			C.TP_CASH: TP(C.CASH),
			C.TP_COAL: TP(C.COAL),
			C.TP_DIESEL: TP(C.DIESEL),
			C.TP_ELECTRIC: TP(C.ELECTRIC),
			
			C.TPC_ADJCOST: adjcost and cargo_throughput/(adjcost*adj_scale),
			C.TPP_ADJCOST: adjcost and profit_throughput/(adjcost*adj_scale),
			C.TPC_CASH: TPc(C.CASH),
			C.TPP_CASH: TPp(C.CASH),
			C.TPC_COAL: TPc(C.COAL),
			C.TPP_COAL: TPp(C.COAL),
			C.TPC_DIESEL: TPc(C.DIESEL),
			C.TPP_DIESEL: TPp(C.DIESEL),
			C.TPC_ELECTRIC: TPc(C.ELECTRIC),
			C.TPP_ELECTRIC: TPp(C.ELECTRIC),
			C.COSTS_RAW: repr(cost),
			
			# train-specific
			C.CD6: towage/(6-length),
			C.CD8: towage/(8-length),
			
			# wagon-specific
			C.COMPOUND_EFFICIENCY: (capacity/length)*(10*capacity/weight_full),
			C.COMPOUND_PROFITABILITY: (profit/length)*(10*profit/weight_full),
			C.DENSITY: weight_full/length,
			C.WT_PER_CARGO: safe_div(weight_full, capacity),
			C.CARGO_UNIT_WT: safe_div(weight_full-weight_empty, capacity),
		}
	except Exception as e:
		e.add_note(f"ID: {vehicle.get(C.ID)}, source: {filename}")
		e.add_note(repr(vehicle))
		raise

def filter_row(vehicle, fields):
	try:
		return {f: vehicle[f] for f in fields}
	except KeyError as e:
		e.add_note(repr(vehicle))
		raise

# This is bad but it's the least repetitive way without rewriting quite a bit
null_row = all_stats({
C.ID: '0', 'vehicle_type': '0', 'name': '', 'weight_full': 1.,
'weight_empty': 1., 'epoch': '0', 'length': 1.
}, '')
all_labels = list(null_row)

train_direct_labels = [
	C.NAME, C.SPEED, C.TRACTION, C.POWER, C.WEIGHT, C.LENGTH, C.ERA
]

train_row_labels = [
	C.NAME, C.SPEED, C.TRACTION, C.POWER, C.WEIGHT, C.LENGTH, C.ERA, C.TOWAGE,
	C.PWT_EMPTY, C.PWT_FULL, C.TOW_PER_LENGTH, C.POWER_PER_LENGTH, C.THROUGHPUT,
	C.CD6, C.CD8, C.SPEED_MPH,
	C.TP_CASH, C.TP_COAL, C.TP_DIESEL, C.TP_ELECTRIC,
	C.CASH, C.COAL, C.DIESEL, C.ELECTRIC,
	C.TP_ADJCOST, C.ADJCOST, # C.COSTS_RAW,
	C.ERAS, C.ID, C.SOURCE
]

wagon_direct_labels = [
	C.NAME, C.TYPE, C.CARGO, C.WEIGHT_EMPTY, C.WEIGHT_FULL, C.LENGTH, C.ERA,
	C.BONUS
]

wagon_row_labels = [
	C.NAME, C.TYPE, C.CARGO, C.WEIGHT_EMPTY, C.WEIGHT_FULL, C.LENGTH, C.ERA,
	C.BONUS, C.CARGO_PER_LENGTH, C.CARGO_PER_WT, C.COMPOUND_EFFICIENCY,
	C.DENSITY, C.PROFITABILITY, C.PROFIT_PER_LENGTH, C.PROFIT_PER_WT,
	C.COMPOUND_PROFITABILITY, C.WT_PER_CARGO, C.CARGO_UNIT_WT,
	C.ERAS, C.ID, C.CID, C.SOURCE,
	C.POWER
]

vehicle_row_labels = [
	C.NAME, C.TYPE, C.CARGO, C.SPEED, C.POWER, C.WEIGHT_EMPTY, C.WEIGHT_FULL,
	C.LENGTH, C.ERA, C.BONUS, C.PWT_EMPTY, C.PWT_FULL, C.THROUGHPUT, C.TP_CARGO,
	C.CARGO_PER_LENGTH, C.PROFITABILITY, C.PROFIT_PER_LENGTH, C.CARGO_UNIT_WT,
	C.SPEED_MPH,
	C.CASH, C.COAL, C.DIESEL, C.ELECTRIC, C.ADJCOST,
	C.TP_ADJCOST, C.TP_CASH, C.TP_COAL, C.TP_DIESEL, C.TP_ELECTRIC,
	C.TPC_ADJCOST, C.TPC_CASH, C.TPC_COAL, C.TPC_DIESEL, C.TPC_ELECTRIC,
	C.TPP_ADJCOST, C.TPP_CASH, C.TPP_COAL, C.TPP_DIESEL, C.TPP_ELECTRIC,
	# C.COSTS_RAW,
	C.ERAS, C.ID, C.CID, C.SOURCE
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
					ret[row[C.NAME].lower()] = {
						'data': val,
						'seen': False
					}
				except KeyError as e:
					e.add_note(f"in: {repr(row)}, source: {filename}")
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

def compare_vehicle(vehicle, expected, label, fields, elementary_fields, fmt, out):
	if expected is None:
		print(
			f"{label} new: {fmt(vehicle)} ID={vehicle[C.ID]}:{vehicle['source']}",
			file=out)
	elif vehicle is None:
		if not '*' in expected[C.NAME]:
			print(f"{label} missing: {fmt(expected)}", file=out)
	else:
		discrepancy = []
		for field in fields:
			try:
				if field in expected \
					and not compare_exp_val(vehicle.get(field), expected[field],
					field):
					discrepancy.append(field)
			except TypeError as e:
				e.add_note(f"{field}: {repr(vehicle.get(field))} {repr(expected[field])}")
				e.add_note(repr(vehicle) + " " + repr(expected))
				raise
		if discrepancy:
			print(
				f"{label} diff: got ({fmt(vehicle)}) expected ({fmt(expected)}) "
				f"ID={vehicle[C.ID]}:{vehicle['source']}",
				file=out)
			print("\t" + "; ".join(
				["{}{}:{},{}".format("!" if f in elementary_fields else "=",
					f, repr(rnd(vehicle[f])), repr(rnd(expected[f])))
					for f in discrepancy]),
				file=out)

ign_fields = [C.NAME, C.ERA, C.ERAS]
def elem(fields):
	return list(filter(lambda x: not x in ign_fields, fields))

def compare_train(vehicle, expected, out):
	fields = [
		C.SPEED, C.POWER, C.WEIGHT, C.LENGTH,
		C.CASH, C.COAL, C.DIESEL, C.ELECTRIC
	]
	def fmt(t):
		try:
			return "{n} ({e}) s={s} p={p} w={w} l={l} c={c}".format(
				n=t[C.NAME], e=t.get(C.ERAS, t[C.ERA]),
				s=rnd(t[C.SPEED]),
				p=rnd(t[C.POWER]), w=rnd(t[C.WEIGHT]),
				l=rnd(t[C.LENGTH]),
				c=f"{t[C.CASH]};{t[C.COAL]}c;{t[C.DIESEL]}d;{t[C.ELECTRIC]}e")
		except KeyError as e:
			e.add_note(repr(t))
			raise
	return compare_vehicle(vehicle, expected, 'train', elem(train_row_labels), train_direct_labels, fmt, out)

def compare_wagon(vehicle, expected, out):
	fields = [
		C.TYPE, C.CARGO, C.WEIGHT_EMPTY,
		C.WEIGHT_FULL, C.LENGTH, C.BONUS
	]
	def fmt(t):
		return "{n} ({e}) t={t} c={c} wu={wu} wl={wl} l={l} b={b} p={p}".format(
			n=t[C.NAME], e=t.get(C.ERAS, t[C.ERA]),
			t=rnd(t[C.TYPE]), c=rnd(t[C.CARGO]),
			wu=rnd(t[C.WEIGHT_EMPTY]), wl=rnd(t[C.WEIGHT_FULL]),
			l=rnd(t[C.LENGTH]), b=rnd(t[C.BONUS]), p=rnd(t.get(C.POWER)))
	return compare_vehicle(vehicle, expected, 'wagon', elem(wagon_row_labels), wagon_direct_labels, fmt, out)

def read_files(files, vfiles):
	idx = 0
	def impl(files, vanilla):
		nonlocal idx
		out = []
		for file in files:
			dom = BeautifulSoup(slurp(file), "lxml")
			for tag in dom.find_all('wagontype'):
				row = all_stats(tag.attrs, file, vanilla)
				row['index'] = idx
				idx = idx + 1
				out.append(row)
		return out
	return impl(vfiles, True) + impl(files, False)


def process_files(table, out, msg, fields, pred, exp, comp, exp_out):
	def impl(outfile, table):
		writer = csv.DictWriter(
			outfile, fieldnames=fields,
			quoting=csv.QUOTE_NONNUMERIC, extrasaction='ignore')
		writer.writeheader()
		for vehicle in (filter_row(row, fields) for row in table if pred(row)):
			writer.writerow(vehicle)
			if exp:
				try:
					name = vehicle[C.NAME].lower()
					e = exp.get(name)
					comp(vehicle, e['data'] if e else None, exp_out)
					if e:
						e['seen'] = True
				except KeyError as e:
					e.add_note(repr(vehicle))
					e.add_note(f"in {vehicle[C.ID]}, source: {vehicle[C.SOURCE]}")
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

def filter_engine(a):
	return int(a['vehicle_type']) == 0 and a.get('fuel_cost')
def filter_wagon(a):
	return int(a['vehicle_type']) == 0 and a.get('cargo')
def filter_vehicle(a):
	return int(a['vehicle_type']) == 1
def filter_aircraft(a):
	return int(a['vehicle_type']) == 3

def run(files, vfiles, train_out, wagon_out, vehicle_out, aircraft_out, univ_out, expected_trains, expected_wagons, unexpected_outstream):
	table = read_files(files, vfiles)

	process_files(table, train_out, "Trains:", train_row_labels,
		filter_engine,
		expected_trains, compare_train, unexpected_outstream)

	process_files(table, wagon_out,"Wagons:", wagon_row_labels,
		filter_wagon,
		expected_wagons, compare_wagon, unexpected_outstream)

	process_files(table, vehicle_out, "Vehicles:", vehicle_row_labels,
		filter_vehicle,
		None, None, None)

	process_files(table, aircraft_out, "Aircraft:", vehicle_row_labels,
		filter_aircraft,
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
		help="Path(s) to individual files for vanilla trains")
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
	parser.add_argument('--props', default=None)
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

def generate_props(props):
	with open(props, 'w') as p:
		lookup = {str(v): k for k, v in C.__dict__.items()}
		fix = lambda s, n: 'C.' + n if n is not None else repr(s)
		print("""from dataclasses import dataclass
from enum import Enum, auto
import constants as C

class Highlight(Enum):
	NONE = auto()
	HIGH = auto()
	LOW = auto()
	PARITY = auto()

@dataclass(kw_only=True, frozen=True)
class ColProps:
	type: type
	highlight: Highlight = Highlight.NONE
	generated: bool = True
	hidden: bool = False

""", end='', file=p)
		print('props = {', file=p)
		for c, d in ({'index': 0} | null_row).items():
			print(f"\t{fix(c, lookup.get(c, None))}: ColProps(type={type(d).__name__}),", file=p)
		print('}', file=p)

def handle_cli(gui):
	warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
	parser = make_arg_parser(gui)
	args = parser.parse_args()
	files = find_files(args.files, args.path)
	vfiles = find_files(args.vanilla, args.vanilla_dir)

	if args.income:
		read_incomes(args.income)

	if args.props:
		generate_props(args.props)

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
