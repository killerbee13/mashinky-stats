from pathlib import Path
import argparse
import csv
import math
import re
import sys
import warnings
from bs4 import BeautifulSoup, SoupStrainer
from bs4 import XMLParsedAsHTMLWarning
from bs4.diagnose import diagnose

def slurp(filename):
	try:
		with open(filename, "r", encoding="utf-8") as f:
			return f.read()
	except UnicodeError:
		with open(filename, "r", encoding="utf-16") as f:
			return f.read()

km_per_mi = 1.609344
traction_scale = 42.1

time_speed = 0.33
tick_rate = 0.1
token_supply = {
	'cash': 1000.0, 'coal': 500.0, 'diesel': 250.0, 'electric': 0.0
}

fuel_per_year = (tick_rate*365)/5.0

adj_scale = 1000
fixed_scale = {'cash': 1000, 'coal': 1000, 'diesel': 1000, 'electric': 1000}
token_by_label = {
	"F1283C03": "coal", "F29BF6C1": "diesel", "F9D8BF64": "electric"}
cargo_by_label = {
	"0BA458C8": "Passenger",	"0F822763": "Mail",  	"3199AA74": "Logs",
	"448DDF23": "Lumber",   	"6ACBCBA9": "Coal",  	"61A13BCE": "Ore",
	"7C13D1C9": "Iron",     	"19CFBDA7": "Oil",   	"53F1B093": "Diesel",
	"B388ED8C": "Goods",    	"94032E35": "Sand",  	"88D1A491": "Steel",
	"C74198A7": "Food",     	"762F8F3E": "Limestone","8DFA75B5": "Cement",
	"9A988702": "Garbage"
}

def rnd(x):
	return math.floor(x*100)/100 if type(x) is float else x

def costs(train):
	raw = re.findall(r'-([0-9.]+)(?:\[([^[]+)\])?;?', train['fuel_cost'])
	return {token_by_label.get(t, "cash"): float(x) for x, t in raw}

def adj_costs(cost):
	cost_adj_d = {
		t: fuel_per_year/x if x != 0 else 2
		for t, x in token_supply.items()
	}
	return [cost.get(t,0)*x/cost_adj_d['cash'] for t, x in cost_adj_d.items()]

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
		type = cargo_by_label.get(vehicle.get('cargo')) or ""
		if vehicle['vehicle_type'] == 0 and power and type == "Passenger":
			type = "Pass. Engine"
		elif vehicle['vehicle_type'] == 0 and power and type == "Mail":
			type = "Mail Engine"
		capacity = float(vehicle.get('capacity', 0))
		weight_empty = float(vehicle['weight_empty'])
		weight_full = float(vehicle['weight_full'])
		
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
		
		traction = math.floor(traction_scale*power/max_speed) if max_speed else 0
		towage = traction-weight_full
		throughput = towage*max_speed
		cargo_throughput = capacity*max_speed
		profit_throughput = profit*max_speed
		
		def TP_c(c, t):
			return (str(t/(cost.get(c, 0)*fixed_scale[c])) if t and cost.get(c)
				else "")
		TP = lambda c: TP_c(c, throughput)
		TPc = lambda c: TP_c(c, cargo_throughput)
		TPp = lambda c: TP_c(c, profit_throughput)
		
		eras = parse_eras(raw_epoch)
		#print(raw_epoch, repr(epochs), eras)
		
		return vehicle | {
			# technical info
			"id": str(vehicle['id']),
			"cargo id": vehicle.get('cargo', ""),
			"source": filename,
			
			# common
			"Name": vehicle['name'].rstrip(),
			"Length (u)": length,
			"Weight (t)": weight_full, 
			"Wt. Loaded (t)": weight_full, 
			"Wt. Unloaded (t)": weight_empty, 
			"Epochs": raw_epoch,
			"Era": eras[0],
			"Eras": eras,
			"Track": vehicle.get('track', 0),
			
			# prime movers
			"Speed (km/h)": max_speed,
			"Speed (mph)": round(max_speed/km_per_mi),
			"Power (hp)": power, 
			"Traction (t)": traction,
			"Towage (t)": towage,
			"Throughput (t*km/hr)": throughput, 
			"P/Wt loaded (hp/t)": power/traction if traction != 0 else 0,
			"P/Wt unloaded (hp/t)": power/weight_full,
			"Tow/length (t/u)": towage/length,
			"Power/length (hp/u)": power/length,
			
			# cargo carriers
			"Type": type,
			"Cargo": capacity, 
			"Bonus": round(100*(bonus-1)) if bonus != 1 else "", 
			"Profitability (Cargo*Bonus)": profit, 
			"Cargo/Length": capacity/length, 
			"Profit/Length": profit/length, 
			"10 Cargo/Wt.": 10*capacity/weight_full, 
			"10 Profit/Wt.": 10*profit/weight_full, 
			
			# units (i.e. power and capacity both != 0)
			"Cargo Throughput": cargo_throughput,
			"Profit Throughput": profit_throughput,
			
			# fuel
			"Adjusted Cost (share of all tokens produced)": adjcost,
			"Cash": cost.get('cash', 0),
			"Coal": cost.get('coal', 0),
			"Diesel": cost.get('diesel', 0),
			"Electric": cost.get('electric', 0),
			
			"TP/AdjCost": adjcost and throughput/(adjcost*adj_scale),
			"TP/Cash": TP('cash'),
			"TP/Coal": TP('coal'),
			"TP/Diesel": TP('diesel'),
			"TP/Electric": TP('electric'),
			
			"TPc/AdjCost": adjcost and cargo_throughput/(adjcost*adj_scale),
			"TPp/AdjCost": adjcost and profit_throughput/(adjcost*adj_scale),
			"TPc/Cash": TPc('cash'),
			"TPp/Cash": TPp('cash'),
			"TPc/Coal": TPc('coal'),
			"TPp/Coal": TPp('coal'),
			"TPc/Diesel": TPc('diesel'),
			"TPp/Diesel": TPp('diesel'),
			"TPc/Electric": TPc('electric'),
			"TPp/Electric": TPp('electric'),
			"Costs (raw)": repr(cost),
			
			# train-specific
			"CD(6) (t/6u)": towage/(6-length),
			"CD(8) (t/8u)": towage/(8-length),
			
			# wagon-specific
			"Compound Efficiency": (capacity/length)*(10*capacity/weight_full), 
			"Compound Profitability": (profit/length)*(10*profit/weight_full), 
			"Density": weight_full/length, 
			"Wt/Cargo": weight_full/capacity if capacity != 0 else 0, 
			"Cargo Unit Wt": (
				(weight_full-weight_empty)/capacity if capacity != 0
				else 0),
		}
	except Exception as e:
		e.add_note(f"ID: {vehicle.get('id')}, source: {filename}")
		raise

def filter_row(vehicle, fields, filename):
	stats = all_stats(vehicle, filename)
	return {f: stats[f] for f in fields}

# This is bad but it's the least repetitive way without rewriting quite a bit
all_labels = list(all_stats({
	'id': '0', 'vehicle_type': 0, 'name': '', 'weight_full': 1,
	'weight_empty': 1, 'epoch': '0', 'length': 1
}, ''))

train_row_labels = [
	"Name", "Speed (km/h)", "Traction (t)", "Power (hp)", "Weight (t)",
	"Length (u)", "Era",
	"Towage (t)", "P/Wt unloaded (hp/t)", "P/Wt loaded (hp/t)",
	"Tow/length (t/u)", "Power/length (hp/u)", "Throughput (t*km/hr)",
	"CD(6) (t/6u)", "CD(8) (t/8u)", "Speed (mph)",
	"TP/Cash", "TP/Coal", "TP/Diesel", "TP/Electric",
	"Cash", "Coal", "Diesel", "Electric",
	"TP/AdjCost", "Adjusted Cost (share of all tokens produced)",
	# "Costs (raw)",
	"Eras", "id", "source"
]

wagon_row_labels = [
	"Name", "Type", "Cargo", "Wt. Unloaded (t)", "Wt. Loaded (t)",
	"Length (u)", "Era", "Bonus",
	"Cargo/Length", "10 Cargo/Wt.", "Compound Efficiency", "Density",
	"Profitability (Cargo*Bonus)", "Profit/Length", "10 Profit/Wt.",
	"Compound Profitability", "Wt/Cargo", "Cargo Unit Wt",
	"Eras", "id", "cargo id", "source"
]

vehicle_row_labels = [
	"Name", "Type", "Cargo", "Speed (km/h)", "Power (hp)",
	"Wt. Unloaded (t)", "Wt. Loaded (t)", "Length (u)", "Era", "Bonus",
	"P/Wt unloaded (hp/t)", "P/Wt loaded (hp/t)",
	"Throughput (t*km/hr)", "Cargo Throughput", "Cargo/Length",
	"Profitability (Cargo*Bonus)", "Profit/Length", "Cargo Unit Wt",
	"Speed (mph)",
	"Cash", "Coal", "Diesel", "Electric",
	"Adjusted Cost (share of all tokens produced)",
	"TP/AdjCost", "TP/Cash", "TP/Coal", "TP/Diesel", "TP/Electric",
	"TPc/AdjCost", "TPc/Cash", "TPc/Coal", "TPc/Diesel", "TPc/Electric",
	"TPp/AdjCost", "TPp/Cash", "TPp/Coal", "TPp/Diesel", "TPp/Electric",
	# "Costs (raw)",
	"Eras", "id", "cargo id", "source"
]

def read_expected(filename):
	ret = {}
	if filename:
		with open(filename, "r", newline='') as file:
			reader = csv.DictReader(file, quoting=csv.QUOTE_NONNUMERIC)
			for row in reader:
				try:
					ret[row['Name'].lower()] = {
						'data': {
							f: v for f, v in row.items()
								if not (type(v) is str and v.startswith('='))
						},
						'seen': False
					}
				except KeyError as e:
					e.add_note(f"in: {repr(row)}, source: {filename}")
					raise
	return ret

def compare_vehicle(vehicle, expected, label, elementary_fields, fmt, out):
	if expected is None:
		print(
			f"{label} new: {fmt(vehicle)} ID={vehicle['id']}:{vehicle['source']}",
			file=out)
	elif vehicle is None:
		print(f"{label} missing: {fmt(expected)}", file=out)
	else:
		discrepancy = []
		for field in elementary_fields:
			if rnd(vehicle.get(field)) != rnd(expected.get(field)):
				discrepancy.append(field)
		if discrepancy:
			print(
				f"{label} diff: got ({fmt(vehicle)}) expected ({fmt(expected)}) "
				f"ID={vehicle['id']}:{vehicle['source']}",
				file=out)
			print("\t" + "; ".join(
				["{}:{},{}".format(f, rnd(vehicle[f]), rnd(expected[f]))
					for f in discrepancy]),
				file=out)

def compare_train(vehicle, expected, out):
	fields = [
		'Speed (km/h)', 'Power (hp)', 'Weight (t)', 'Length (u)',
		'Cash', 'Coal', 'Diesel', 'Electric'
	]
	def fmt(t):
		return "{n} ({e}) s={s} p={p} w={w} l={l} c={c}".format(
			n=t['Name'], e=t.get('Eras', t['Era']), s=rnd(t['Speed (km/h)']),
			p=rnd(t['Power (hp)']), w=rnd(t['Weight (t)']),
			l=rnd(t['Length (u)']),
			c=f"{t['Cash']};{t['Coal']}c;{t['Diesel']}d;{t['Electric']}e")
	return compare_vehicle(vehicle, expected, 'train', fields, fmt, out)

def compare_wagon(vehicle, expected, out):
	fields = [
		'Type', 'Cargo', 'Wt. Unloaded (u)', 'Wt. Loaded (u)', 'Length (u)',
		'Bonus'
	]
	def fmt(t):
		return "{n} ({e}) t={t} c={c} wu={wu} wl={wl} l={l} b={b}".format(
			n=t['Name'], e=t.get('Eras', t['Era']),
			t=rnd(t['Type']), c=rnd(t['Cargo']),
			wu=rnd(t['Wt. Unloaded (t)']), wl=rnd(t['Wt. Loaded (t)']),
			l=rnd(t['Length (u)']), b=rnd(t['Bonus']))
	return compare_vehicle(vehicle, expected, 'wagon', fields, fmt, out)

def process_files(files, out, msg, fields, pred, exp, comp, exp_out):
	def impl(outfile):
		writer = csv.DictWriter(
			outfile, fieldnames=fields,
			quoting=csv.QUOTE_NONNUMERIC, extrasaction='ignore')
		writer.writeheader()
		for file in files:
			dom = BeautifulSoup(slurp(file), "lxml")
			#print(dom.prettify())
			
			for tag in dom.find_all('wagontype'):
				#print("tag: ", tag.attrs['vehicle_type'], tag.attrs['name'])
				if pred(tag.attrs):
					vehicle = filter_row(tag.attrs, fields, file)
					writer.writerow(vehicle)
					if exp:
						try:
							name = vehicle['Name'].lower()
							e = exp.get(name)
							comp(vehicle, e['data'] if e else None, exp_out)
							if e:
								e['seen'] = True
						except KeyError as e:
							e.add_note(f"in {vehicle['id']}, source: {file}")
							raise
		if exp:
			for vehicle in (
				vehicle['data'] for vehicle in exp.values()
				if not vehicle['seen']
			):
				comp(None, vehicle, exp_out)
	if out == '-':
		print(msg)
		impl(sys.stdout)
	else:
		with open(out, 'w', newline='') as outfile:
			impl(outfile)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('files', nargs='*',
		help='Paths to individual xml files to parse')
	parser.add_argument('-p', '--path', action='append', default=[],
		help='Path(s) to mods root directory')
	parser.add_argument('-t', '--train_out', default='-')
	parser.add_argument('-w', '--wagon_out', default='-')
	parser.add_argument('-r', '--vehicle_out', default='-')
	parser.add_argument('-a', '--aircraft_out', default='-')
	parser.add_argument('-u', '--univ_out')
	parser.add_argument('-T', '--expected_trains')
	parser.add_argument('-W', '--expected_wagons')
	parser.add_argument('-d', '--unexpected_out', default='-')
	parser.add_argument('-i', '--income')
	args = parser.parse_args()
	
	files = [Path(f) for f in args.files]
	for file in files:
		if not file.exists() or not file.is_file():
			raise IOError('Invalid file ' + str(file))
	
	for raw_path in args.path:
		path = Path(raw_path)
		if not path.exists or not path.is_dir():
			raise IOError('Invalid path ' + str(path))
		for file in path.glob('*/config/wagon_types.xml'):
			files.append(file)
	
	if args.income:
		parsed = re.fullmatch(
			r'(\d+)[;, ](\d+)c[;, ](\d+)d[;, ](\d+)e', args.income)
		if parsed:
			token_supply['cash'] = int(parsed.group(1))
			token_supply['coal'] = int(parsed.group(2))
			token_supply['diesel'] = int(parsed.group(3))
			token_supply['electric'] = int(parsed.group(4))
		else:
			raise ValueError("Could not parse --income argument: "
				+ repr(args.income))
	
	with (sys.stdout
	      if args.unexpected_out == '-'
			else open(args.unexpected_out, 'w', newline='')
	as unexpected_outstream):
		expected_trains = read_expected(args.expected_trains)
		expected_wagons = read_expected(args.expected_wagons)
		
		warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
		strainer = SoupStrainer("WagonType")
		
		process_files(files, args.train_out, "Trains:", train_row_labels,
			lambda a: int(a['vehicle_type']) == 0 and a.get('fuel_cost'),
			expected_trains, compare_train, unexpected_outstream)
		
		process_files(files, args.wagon_out,"Wagons:", wagon_row_labels,
			lambda a: int(a['vehicle_type']) == 0 and a.get('cargo'),
			expected_wagons, compare_wagon, unexpected_outstream)

		process_files(files, args.vehicle_out, "Vehicles:", vehicle_row_labels,
			lambda a: int(a['vehicle_type']) == 1,
			None, None, None)
		
		process_files(files, args.aircraft_out, "Aircraft:", vehicle_row_labels,
			lambda a: int(a['vehicle_type']) == 3,
			None, None, None)
		
		if args.univ_out:
			process_files(files, args.univ_out, "All:", all_labels,
				lambda a: True,
				None, None, None)
	
if __name__ == '__main__':
	main()
