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
token_supply = {'cash': 1000.0, 'coal': 500.0, 'diesel': 250.0, 'electric': 0.0}

fuel_per_year = (tick_rate*365)/5.0

adj_scale = 1000
fixed_scale = {'cash': 1000, 'coal': 1000, 'diesel': 1000, 'electric': 1000}
token_by_label = {
	"F1283C03": "coal", "F29BF6C1": "diesel", "F9D8BF64": "electric"}
cargo_by_label = {
	"0BA458C8": "Passenger", "0F822763": "Mail", "3199AA74": "Logs", "448DDF23": "Lumber", "6ACBCBA9": "Coal", "61A13BCE": "Ore", "7C13D1C9": "Iron", "19CFBDA7": "Oil", "53F1B093": "Diesel", "B388ED8C": "Goods", "94032E35": "Sand", "88D1A491": "Steel", "C74198A7": "Food", "762F8F3E": "Limestone", "8DFA75B5": "Cement", "9A988702": "Garbage"
}

def costs(train):
	raw = re.findall(r'-([0-9.]+)(?:\[([^[]+)\])?;?', train['fuel_cost'])
	return {token_by_label.get(t, "cash"): float(x) for x, t in raw}

def cost_adj(cost):
	cost_adj = {t: fuel_per_year/x if x != 0 else 2 for t, x in token_supply.items()}
	return sum([cost.get(t,0)*x/cost_adj['cash'] for t, x in cost_adj.items()])

train_row_labels = [
	"Name", "Speed (km/h)", "Traction (t)", "Power (hp)", "Weight (t)", "Length (u)", "Era", "Towage (t)", "P/Wt unloaded (hp/t)", "P/Wt loaded (hp/t)", "Tow/length (t/u)", "Power/length (hp/u)", "Throughput (t*km/hr)", "CD(6) (t/6u)", "CD(8) (t/8u)", "Speed (mph)",
	"TP/Cash", "TP/Coal", "TP/Diesel", "TP/Electric", "Cash", "Coal", "Diesel", "Electric", "TP/AdjCost", "Adjusted Cost (share of all tokens produced)",
	# "Costs (raw)",
	"id", "source"
]

def train_to_row(train, filename):
	try:
		length = float(train.get('length',0)) + float(train.get('head_length', 0)) + float(train.get('tail_length',0))
		power = float(train['power'])
		max_speed = float(train['max_speed'])
		weight_full = float(train['weight_full'])
		traction = math.floor(traction_scale*power/max_speed)
		towage = traction-weight_full
		raw_epoch = train['epoch']
		throughput = towage*max_speed
		cost = costs(train)
		adjcost = cost_adj(cost)
		
		TP = lambda c: str(throughput/(cost.get(c, 0)*fixed_scale[c])) if cost.get(c) else ""
		
		return {
			"Name": train['name'],
			"Speed (km/h)": max_speed,
			"Traction (t)": traction,
			"Power (hp)": power, 
			"Weight (t)": weight_full, 
			"Length (u)": length,
			"Era": raw_epoch, # wrong
			"Towage (t)": towage,
			"P/Wt unloaded (hp/t)": power/traction if traction != 0 else 0,
			"P/Wt loaded (hp/t)": power/weight_full,
			"Tow/length (t/u)": towage/length,
			"Power/length (hp/u)": power/length,
			"Throughput (t*km/hr)": throughput, 
			"CD(6) (t/6u)": towage/(6-length),
			"CD(8) (t/8u)": towage/(8-length),
			"Speed (mph)": round(max_speed*km_per_mi),
			"Costs (raw)": repr(cost), # wrong
			"TP/Cash": TP('cash'),
			"TP/Coal": TP('coal'),
			"TP/Diesel": TP('diesel'),
			"TP/Electric": TP('electric'),
			"Cash": cost.get('cash'),
			"Coal": cost.get('coal'),
			"Diesel": cost.get('diesel'),
			"Electric": cost.get('electric'),
			"TP/AdjCost": throughput/(adjcost*adj_scale),
			"Adjusted Cost (share of all tokens produced)": adjcost,
			"id": train['id'],
			"source": filename,
		}
	except Exception as e:
		e.add_note(f"ID: {train.get('id')}, source: {filename}")
		e.add_note(repr(train))
		raise

wagon_row_labels = [
	"Name", "Type", "Cargo", "Wt. Unloaded", "Wt. Loaded", "Length", "Era", "Bonus", "Cargo/Length", "10 Cargo/Wt. Loaded", "Compound Efficiency", "Density", "Profitability", "Profit/Length", "10 Profit/Wt", "Compound Profitability", "Wt/Cargo", "Cargo Unit Wt",
	"id", "cargo id", "source"
]

def wagon_to_row(wagon, filename):
	try:
		length = float(wagon.get('length',0)) + float(wagon.get('head_length', 0)) + float(wagon.get('tail_length',0))
		capacity = float(wagon.get('capacity', 0))
		weight_full = float(wagon['weight_full'])
		weight_empty = float(wagon['weight_empty'])
		raw_epoch = wagon['epoch']
		
		effect = re.fullmatch(r'(?:profit\[[^]]*\])\*([0-9]*.?[0-9]*)', wagon.get('effect', ""))
		bonus = 1
		if effect:
			bonus = float(effect.group(1))
		profit = capacity*bonus
		
		
		return {
			"Name": wagon['name'],
			"Type": cargo_by_label[wagon['cargo']],
			"Cargo": capacity, 
			"Wt. Unloaded": weight_empty, 
			"Wt. Loaded": weight_full, 
			"Length": length, 
			"Era": raw_epoch, 
			"Bonus": 100*(bonus-1) or "", 
			"Cargo/Length": capacity/length, 
			"10 Cargo/Wt. Loaded": 10*capacity/weight_full, 
			"Compound Efficiency": (capacity/length)*(10*capacity/weight_full), 
			"Density": weight_full/length, 
			"Profitability": profit, 
			"Profit/Length": profit/length, 
			"10 Profit/Wt": 10*profit/weight_full, 
			"Compound Profitability": (profit/length)*(10*profit/weight_full), 
			"Wt/Cargo": weight_full/capacity if capacity != 0 else 0, 
			"Cargo Unit Wt": (weight_full-weight_empty)/capacity if capacity != 0 else 0,
			"id": wagon['id'],
			"cargo id": wagon['cargo'],
			"source": filename
		}
		return [wagon['name'], wagon['cargo'], cargo_by_label[wagon['cargo']], wagon['id']]
	except Exception as e:
		e.add_note(f"ID: {wagon.get('id')}, source: {filename}")
		raise

def read_expected(filename):
	ret = {}
	if filename:
		with open(filename, "r", newline='') as file:
			reader = csv.DictReader(file, quoting=csv.QUOTE_NONNUMERIC)
			for row in reader:
				try:
					ret[row['Name'].lower()] = {
						'data': {f: v for f, v in row.items() if not (type(v) is str and v.startswith('='))},
						'seen': False
					}
				except KeyError as e:
					e.add_note(f"in: {repr(row)}, source: {filename}")
					raise
	return ret

def compare_train(train, expected):
	elementary_fields = ['Speed (km/h)', 'Power (hp)', 'Weight (t)', 'Length (u)', 'Cash', 'Coal', 'Diesel', 'Electric']
	r = lambda x: round(x*100)/100 if type(x) is float else x
	def simple(t):
		return f"{t['Name']} s={r(t['Speed (km/h)'])} p={r(t['Power (hp)'])} w={r(t['Weight (t)'])} l={r(t['Length (u)'])} e={t['Era']} c={t['Cash']};{t['Coal']}c;{t['Diesel']}d;{t['Electric']}e"
	if expected is None:
		print(f"new train: {simple(train)} ID={train['id']}:{train['source']}")
	elif train is None:
		print(f"missing train: {simple(expected)}")
	else:
		discrepancy = []
		for field in elementary_fields:
			if r(train.get(field)) != r(expected.get(field)):
				discrepancy.append(field)
		if discrepancy:
			print(f"train discrepancy: got ({simple(train)}) expected ({simple(expected)}) ID={train['id']}:{train['source']}")
			print("\t" + ", ".join(["{}:{},{}".format(f, r(train[f]), r(expected[f])) for f in discrepancy]))

def compare_wagon(wagon, expected):
	elementary_fields = ['Type', 'Cargo', 'Wt. Unloaded', 'Wt. Loaded', 'Length', 'Bonus']
	r = lambda x: round(x*100)/100 if type(x) is float else x
	def simple(t):
		return f"{t['Name']} t={r(t['Type'])} c={r(t['Cargo'])} wu={r(t['Wt. Unloaded'])} wl={r(t['Wt. Loaded'])} l={r(t['Length'])} e={t['Era']} b={r(t['Bonus'])}"
	if expected is None:
		print(f"new wagon: {simple(wagon)} ID={wagon['id']}:{wagon['source']}")
	elif wagon is None:
		print(f"missing wagon: {simple(expected)}")
	else:
		discrepancy = []
		for field in elementary_fields:
			if r(wagon.get(field)) != r(expected.get(field)):
				discrepancy.append(field)
		if discrepancy:
			print(f"wagon discrepancy: got ({simple(wagon)}) expected ({simple(expected)}) ID={wagon['id']}:{wagon['source']}")
			print("\t" + ", ".join(["{}:{},{}".format(f, r(wagon[f]), r(expected[f])) for f in discrepancy]))
	pass

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--path', help='Path to mods root directory', action='append', default=[])
	parser.add_argument('-t', '--train_out', default='-')
	parser.add_argument('-w', '--wagon_out', default='-')
	parser.add_argument('-T', '--expected_trains')
	parser.add_argument('-W', '--expected_wagons')
	parser.add_argument('files', nargs='*', help='Paths to additional individual xml files to parse')
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
	
	
	
	with (
		sys.stdout if args.train_out == '-' else open(args.train_out, 'w', newline='') as train_outstream,
		sys.stdout if args.wagon_out == '-' else open(args.wagon_out, 'w', newline='') as wagon_outstream
	):
		train_out = csv.DictWriter(train_outstream, fieldnames=train_row_labels, quoting=csv.QUOTE_NONNUMERIC, extrasaction='ignore')
		wagon_out = csv.DictWriter(wagon_outstream, fieldnames=wagon_row_labels, quoting=csv.QUOTE_NONNUMERIC, extrasaction='ignore')
		expected_trains = read_expected(args.expected_trains)
		expected_wagons = read_expected(args.expected_wagons)
		
		warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
		strainer = SoupStrainer("WagonType")
		if args.train_out == '-':
			print("Trains:")
		train_out.writeheader()
		for file in files:
			dom = BeautifulSoup(slurp(file), "lxml")
			#print(dom.prettify())
			
			for tag in dom.find_all('wagontype'):
				#print("tag: ", tag.attrs['vehicle_type'], tag.attrs['name'])
				if int(tag.attrs['vehicle_type']) == 0 and tag.attrs.get('fuel_cost'):
					train = train_to_row(tag.attrs, file)
					train_out.writerow(train)
					if expected_trains:
						try:
							name = train['Name'].lower()
							expected = expected_trains.get(name)
							compare_train(train, expected['data'] if expected else None)
							if expected:
								expected['seen'] = True
						except KeyError as e:
							e.add_note(f"in {train['id']}, source: {file}")
							raise
		
		for train in [train['data'] for train in expected_trains.values() if not train['seen']]:
			compare_train(None, train)
		
		if args.wagon_out == '-':
			print("Wagons:")
		wagon_out.writeheader()
		for file in files:
			dom = BeautifulSoup(slurp(file), "lxml")
			
			for tag in dom.find_all('wagontype'):
				#print("wagon: ", wagon.attrs)
				if int(tag.attrs['vehicle_type']) == 0 and tag.attrs.get('cargo'):
					wagon = wagon_to_row(tag.attrs, file)
					wagon_out.writerow(wagon)
					if expected_wagons:
						try:
							name = wagon['Name'].lower()
							expected = expected_wagons.get(name)
							compare_wagon(wagon, expected['data'] if expected else None)
							if expected:
								expected['seen'] = True
						except KeyError as e:
							e.add_note(f"in {wagon['id']}, source: {file}")
							raise
		
		for wagon in [wagon['data'] for wagon in expected_wagons.values() if not wagon['seen']]:
			compare_wagon(None, wagon)
	
if __name__ == '__main__':
	main()
