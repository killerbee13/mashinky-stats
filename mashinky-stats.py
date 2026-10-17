import argparse
from pathlib import Path
from bs4 import BeautifulSoup, SoupStrainer, UnicodeDammit
from bs4.diagnose import diagnose
from bs4 import XMLParsedAsHTMLWarning
import warnings
import csv
import re
import sys
import math

km_per_mi = 1.609344
traction_scale = 42.1

time_speed = 0.33
tick_rate = 0.1
token_supply = {'cash': 1000, 'coal': 500, 'diesel': 250, 'electric': 0}

def fuel_per_year():
	ticks_per_year = tick_rate*365
	return ticks_per_year/5

adj_scaling_factor = 1000
fixed_scaling_factor = {'cash': 1000, 'coal': 1000, 'diesel': 1000, 'elec': 1000}
token_by_label = {
	"F1283C03": "coal", "F1283C03": "diesel", "F29BF6C1": "electric"}
cargo_by_label = {
	"0BA458C8": "Passengers", "0F822763": "Mail", "3199AA74": "Logs", "448DDF23": "Lumber", "6ACBCBA9": "coal", "61A13BCE": "Ore", "7C13D1C9": "Iron", "19CFBDA7": "Oil", "53F1B093": "Diesel", "B388ED8C": "Goods", "94032E35": "Sand", "88D1A491": "Steel", "C74198A7": "Food", "762F8F3E": "Limestone", "8DFA75B5": "Cement", 
}

def costs(train):
	raw = re.findall(r'-(\d+)(?:\[([^[]+)\])?;?', train['fuel_cost'])
	return {token_by_label.get(t, "cash"): x for x, t in raw}

def cost_adj():
	cost_adj = {t: fuel_per_year/x if x != 0 else 2 for t, x in token_supply}
	return {t: cost_adj['cash']/x for t, x in cost_adj}

def train_to_row(train):
	length = float(train.get('length',"0")) + float(train.get('length_head', "0")) + float(train.get('length_tail',"0"))
	power = int(train['power'])
	max_speed = int(train['max_speed'])
	weight_full = int(train['weight_full'])
	traction = math.floor(traction_scale*power/max_speed)
	towage = traction-weight_full
	raw_epoch = train['epoch']
	throughput = towage*max_speed
	
	return [
		train['name'],
		max_speed,
		traction,
		power, 
		weight_full, 
		length,
		raw_epoch, # wrong
		towage,
		power/traction if traction != 0 else 0,
		power/weight_full,
		towage/length,
		power/length,
		throughput, 
		towage/(6-length),
		towage/(8-length),
		round(max_speed*km_per_mi),
		repr(costs(train)), # wrong
	]

def wagon_to_row(wagon):
	return [wagon['name'], wagon['cargo'], cargo_by_label[wagon['cargo']]]

def is_train(tag):
	return True if tag.get('fuel_cost') else False

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--path', help='Path to mods root directory', action='append', default=[])
	parser.add_argument('-t', '--train_out', default='-')
	parser.add_argument('-w', '--wagon_out', default='-')
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
	
	train_outstream = sys.stdout if args.train_out == '-' else open(args.train_out, 'w', newline='')
	train_out = csv.writer(train_outstream)
	wagon_outstream = sys.stdout if args.wagon_out == '-' else open(args.wagon_out, 'w', newline='')
	wagon_out = csv.writer(wagon_outstream)
	
	warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
	strainer = SoupStrainer("WagonType")
	for file in files:
		dom = BeautifulSoup(open(file, "rb"), "lxml")
		# print(dom.prettify())
		
		if args.train_out == '-':
			print("Trains:")
		for tag in dom.find_all('wagontype'):
			#print("wagon: ", wagon.attrs)
			if tag.attrs.get('fuel_cost'):
				train_out.writerow(train_to_row(tag.attrs))
		
		if args.wagon_out == '-':
			print("Wagons:")
		for tag in dom.find_all('wagontype'):
			#print("wagon: ", wagon.attrs)
			if tag.attrs.get('cargo'):
				wagon_out.writerow(wagon_to_row(tag.attrs))
	
if __name__ == '__main__':
	main()
