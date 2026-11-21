from pathlib import Path
import argparse
import csv
import re
import sys
import warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

import constants as C
from row import (Row, tcoords, token_supply, parse_eras, rnd,
	train_row_labels, wagon_row_labels, vehicle_row_labels,
	train_direct_labels, wagon_direct_labels, all_labels)

def slurp(filename):
	try:
		with open(filename, "r", encoding="utf-8") as f:
			return f.read()
	except UnicodeError:
		with open(filename, "r", encoding="utf-16") as f:
			return f.read()

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
				#print(f"file {file}:")
				dom = BeautifulSoup(slurp(file), "lxml")
				for tag in dom.find_all('wagontype'):
					#print(f"tag {tag['name']}")
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
	#print(repr(coords))

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
		parser.add_argument('--cmap', action='append', default=[])
		parser.add_argument('-c', '--color')
		parser.add_argument('-style')
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
