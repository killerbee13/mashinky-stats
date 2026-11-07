from pathlib import Path
import argparse
import csv
import math
import re
import sys
import warnings
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import constants as C

def slurp(filename):
	try:
		with open(filename, "r", encoding="utf-8") as f:
			return f.read()
	except UnicodeError:
		with open(filename, "r", encoding="utf-16") as f:
			return f.read()

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


def rnd(x, recip_tol=100):
	return math.floor(x*recip_tol)/recip_tol if type(x) is float else x

def costs(train):
	raw = re.findall(r'-([0-9.]+)(?:\[([^[]+)\])?;?', train['fuel_cost'])
	return {token_by_label.get(t, C.CASH): float(x) for x, t in raw}

def adj_costs(cost):
	cost_adj_d = {
		t: fuel_per_year/x if x != 0 else 2
		for t, x in token_supply.items()
	}
	return [cost.get(t,0)*x/cost_adj_d[C.CASH] for t, x in cost_adj_d.items()]

def cost_adj(cost):
	return sum(adj_costs(cost))

def parse_eras(raw_epoch):
	t_eras = [0]*8
	epochs = re.findall(r'([0-9]+)(?:-([0-9]+))?,?+', raw_epoch)
	for r in epochs:
		for e in range(int(r[0]), int(r[1] if r[1] else r[0])+1):
			if e < len(t_eras):
				t_eras[e] = e
	return "".join([str(e) for e in t_eras if e]) or '0'

def all_stats(vehicle, filename):
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
				else "")
		TP = lambda c: TP_c(c, throughput)
		TPc = lambda c: TP_c(c, cargo_throughput)
		TPp = lambda c: TP_c(c, profit_throughput)
		
		eras = parse_eras(raw_epoch)
		#print(raw_epoch, repr(epochs), eras)
		
		return vehicle | {
			# technical info
			C.ID: str(vehicle[C.ID]),
			C.CID: str(vehicle.get('cargo', "")),
			C.SOURCE: str(filename),
			
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
			C.PWT_FULL: power/traction if traction != 0 else 0,
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
			C.CASH: cost.get(C.CASH, 0),
			C.COAL: cost.get(C.COAL, 0),
			C.DIESEL: cost.get(C.DIESEL, 0),
			C.ELECTRIC: cost.get(C.ELECTRIC, 0),
			
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
			C.WT_PER_CARGO: weight_full/capacity if capacity != 0 else 0,
			C.CARGO_UNIT_WT: (
				(weight_full-weight_empty)/capacity if capacity != 0
				else 0),
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
all_labels = list(all_stats({
	C.ID: '0', 'vehicle_type': '0', 'name': '', 'weight_full': 1,
	'weight_empty': 1, 'epoch': '0', 'length': 1
}, ''))

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

def read_files(files):
	out = []
	for file in files:
		dom = BeautifulSoup(slurp(file), "lxml")
		for tag in dom.find_all('wagontype'):
			out.append(all_stats(tag.attrs, file))
	return out


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

def run(files, train_out, wagon_out, vehicle_out, aircraft_out, univ_out, expected_trains, expected_wagons, unexpected_outstream):
	table = read_files(files)

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

	if args.income:
		read_incomes(args.income)
	return args, files

def main():
	args, files = handle_cli(False)
	with (sys.stdout
	      if args.unexpected_out == '-'
			else open(args.unexpected_out, 'w', newline='')
	as unexpected_outstream):
		expected_trains = read_expected(args.expected_trains)
		expected_wagons = read_expected(args.expected_wagons)
		
		run(files, args.train_out, args.wagon_out, args.vehicle_out, args.aircraft_out, args.univ_out, expected_trains, expected_wagons, unexpected_outstream)
	
if __name__ == '__main__':
	main()
