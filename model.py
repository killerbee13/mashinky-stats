# This Python file uses the following encoding: utf-8

import builtins
import pathlib
import types
import typing
import sys
import time
import itertools

from PySide6.QtCore import QObject, Qt, QSortFilterProxyModel
from PySide6.QtSql import (QSqlQuery, QSqlDatabase, QSqlRelationalTableModel)
from PySide6.QtWidgets import QApplication, QTableView, QAbstractItemView

import row
from row import Row, to_sql, token_supply, fuel_per_year, fixed_scale, adj_scale#, time_speed, tick_rate
from mashinky_stats import handle_cli, find_files, read_files

def createConnection():
	db = QSqlDatabase.addDatabase("QSQLITE")
	db.setDatabaseName(":memory:")
	db.setConnectOptions("QSQLITE_ENABLE_REGEXP")
	if not db.open():
		raise ValueError(db.lastError())
	return db





def createView(title, model):
	table_view = QTableView()
	table_view.setModel(model)
	table_view.setWindowTitle(title)
	table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
	table_view.setSortingEnabled(True)

	return table_view


def typename(field, t):
	match t:
		case builtins.str | pathlib.Path:
			if field in ['id', 'cid', 'icon', 'icon_color']:
				return "HEX"
			return 'TEXT'
		case builtins.int:
			if field == 'index':
				return "INTEGER PRIMARY KEY"
			else:
				return "INTEGER"
		case builtins.float:
			if field in ['power', 'traction', 'towage', 'throughput',
				'cash', 'coal', 'diesel', 'electric', 'bonus',
				'cargo_throughput', ]\
				or field.startswith('weight') or field.startswith('max_speed'):
				return "INTEGER"
			else:
				return "FLOAT"
		case builtins.bool:
			return 'BOOLEAN'
		case T if typing.get_args(T):
			match typing.get_args(T):
				case [U, types.NoneType]:
					return typename(field, U)
				case [types.NoneType, U]:
					return typename(field, U)
				case _:
					return 'BLOB'
		case typing.Any:
			if field.startswith('max_speed'):
				return 'INTEGER'
			return 'BLOB'
		case builtins.dict:
			return 'JSON'
		case _:
			return 'BLOB'
def constraints(field):
	if Row.__dict__[field].is_default():
		return f" DEFAULT {to_sql(Row.__dict__[field].default)}"
	return ''
def filter_kw(field):
	if field in ['index', 'set']:
		return f'{field}_'
	return field
def field_to_sql(field):
	if field in ['adjcost', 'TP_adjcost']:
		return f"\t\t{filter_kw(field)} FLOAT"
	ret = ''
	if Row.__dict__[field].sql == False:
		return
	elif field == 'cost':
		ret += "\t\tcost JSON"
		return ret
	ret += f"\t\t{filter_kw(field)} "\
		f"{typename(field, Row.__dict__[field].annotation)}"
	if field in ['eras', 'effect']:
		pass
	if Row.is_generated(field):
		ret += f" AS ({Row.__dict__[field].generator or '0'}) STORED"
	else:
		ret += f"{constraints(field)}"
	return ret

def create_table():
	fs = [field_to_sql(f) for f in Row.keys()]
	return '\n' + ',\n'.join((f for f in fs if f)) + '\n'
def insert_cols():
	fs = list(filter(lambda f: f in ['eras', 'effect']
		or (not Row.is_generated(f) and Row.__dict__[f].sql), Row.keys()))
	cs = list(map(filter_kw,fs))
	return fs,cs
def prepare_query():
	_,cs = insert_cols()
	cols = ', '.join(cs)
	params = ', '.join(f':{f}' for f in cs)
	ret = f"INSERT INTO data({cols}) VALUES({params})"
	return ret
def bind_query(query, r):
	fs,cs = insert_cols()
	#print(f'{fs}, {cs}')
	for f,c in zip(fs, cs):
		#print(f':{c} = {r[f]}')
		query.bindValue(f':{c}', r[f])

def check_exec(query, *args):
	if not query.exec(*args):
		raise ValueError(query.lastError())
def createRelationalTables(db):
	query = QSqlQuery(db)
	check = lambda *args: check_exec(query, *args)

	check("""CREATE TABLE params(
		name TEXT PRIMARY KEY,
		value FLOAT)""")
	#check(f"INSERT INTO params values('time_speed', {time_speed})")
	#check(f"INSERT INTO params values('tick_rate', {tick_rate})")
	check(f"INSERT INTO params values('fuel_per_year', {fuel_per_year})")

	check(f"""CREATE TABLE budget(
		name TEXT PRIMARY KEY,
		value INT NOT NULL,
		adjusted FLOAT AS
			(iif(value, {fuel_per_year}/value, 2))
		)""")

	check(f"INSERT INTO budget VALUES('Cash', {token_supply['Cash']})")
	check(f"INSERT INTO budget VALUES('Coal', {token_supply['Coal']})")
	check(f"INSERT INTO budget VALUES('Diesel', {token_supply['Diesel']})")
	check(f"INSERT INTO budget VALUES('Electric', {token_supply['Electric']})")

	def TP1(c, t):
		return f"iif({c.lower()} != 0, {t}/({c.lower()}*{fixed_scale[c]}), '')"
	def TP_ac(t):
		return f"iif(adjcost != 0, {t}/(adjcost*{adj_scale}), 0)"
	def TP(cur):
		return TP1(cur, 'throughput')
	def TP_col(cur, fun):
		return f"\t\t{cur} FLOAT AS ({fun}) STORED,\n"
	def TPcp(cur):
		return TP_col('TPc_'+cur.lower(), TP1(cur, 'cargo_throughput'))\
			+   TP_col('TPp_'+cur.lower(), TP1(cur, 'profit_throughput'))
	currencies = ['Cash', 'Coal', 'Diesel', 'Electric']
	TP_cols = TP_col('TP_adjcost', TP_ac('throughput')) \
		+ ''.join((TP_col('TP_'+cur.lower(), TP(cur)) for cur in currencies)) \
		+ TP_col('TPc_adjcost', TP_ac('cargo_throughput')) \
		+ TP_col('TPp_adjcost', TP_ac('profit_throughput')) \
		+ ''.join((TPcp(cur) for cur in currencies))
	#print(TP_cols)

	field_strs = create_table()
	#print(field_strs)

	table = f"""
		"index" INTEGER PRIMARY KEY,
		name TEXT,
		source TEXT DEFAULT '',
		vanilla BOOLEAN DEFAULT FALSE,
		id HEX,
		cid HEX DEFAULT '',
		vehicle_type INTEGER,
		track INTEGER default 0,
		weight_full INTEGER,
		weight_empty INTEGER,
		epoch TEXT DEFAULT '',
		eras INTEGER,
		era INTEGER,
		icon TEXT DEFAULT '',
		icon_texture TEXT DEFAULT '',
		icon_color TEXT DEFAULT '',
		length_b FLOAT DEFAULT 0,
		length_head FLOAT DEFAULT 0,
		length_tail FLOAT DEFAULT 0,
		length FLOAT AS (length_b + length_head + length_tail),
		depot_upgrade INTEGER,
		flags TEXT DEFAULT '',
		"set" TEXT DEFAULT '',
		power INTEGER DEFAULT 0,
		max_speed INTEGER DEFAULT 0,
		max_speed_mph INTEGER AS (round(max_speed/1.609344)),
		max_speed_reverse INTEGER,
		max_speed_reverse_mph INTEGER AS (round(max_speed_reverse/1.609344)),
		bidirectional INTEGER DEFAULT NULL,
		traction AS (floor((power*42.1)/max_speed)),
		towage AS (traction - weight_full),
		throughput AS (towage*max_speed),
		raw_cost TEXT DEFAULT '',
		cost JSON,
		cash INTEGER AS (cost->>'Cash'),
		coal INTEGER AS (cost->>'Coal'),
		diesel INTEGER AS (cost->>'Diesel'),
		electric INTEGER AS (cost->>'Electric'),
		adjcost FLOAT,
		capacity INTEGER DEFAULT 0,
		ctype TEXT AS (0),
		raw_effect TEXT DEFAULT '',
		effect FLOAT AS (1),
		bonus FLOAT AS (round(100*(effect-1))),
		runway_length_needed INTEGER DEFAULT NULL,
		pwt_empty FLOAT AS (power/weight_empty),
		pwt_full FLOAT AS (power/weight_full),
		power_per_length FLOAT AS (power/length),
		pwt_loaded FLOAT AS (power/traction),
		tow_per_length FLOAT AS (towage/length),
		profit FLOAT AS (capacity*effect),
		cargo_per_length FLOAT AS (capacity/length),
		profit_per_length FLOAT AS (profit/length),
		cargo_per_wt FLOAT AS (10*capacity/weight_full),
		profit_per_wt FLOAT AS (10*profit/weight_full),
		cargo_throughput FLOAT AS (capacity*max_speed),
		profit_throughput FLOAT AS (profit*max_speed),
		CD6 FLOAT AS (towage/(6-length)),
		CD8 FLOAT AS (towage/(8-length)),
{TP_cols}
		compound_efficiency FLOAT AS (0),
		compound_profitability FLOAT AS (0),
		density FLOAT AS (weight_full/length),
		wt_per_cargo FLOAT AS (weight_full/capacity),
		cargo_unit_wt FLOAT AS ((weight_full-weight_empty)/capacity)
"""
	with open('gen.sql', 'w') as f:
		print(f'CREATE TABLE data({field_strs})', file=f)
	with open('manual.sql', 'w') as f:
		print(f'CREATE TABLE data({table})', file=f)
	check(f'CREATE TABLE data({field_strs})')
#	check("""INSERT INTO data(index_, name, source, vanilla, id, cid,
#		vehicle_type, track, weight_full, weight_empty, epoch, eras, icon,
#		icon_texture, icon_color, length_b, length_head, length_tail, power,
#		max_speed, max_speed_reverse, raw_cost, cost, capacity, raw_effect,
#		runway_length_needed)
#		VALUES(10, '0-4-0 Elishka', 'elishka.xml', TRUE, '00123456', NULL, 0, 0,
#		18, 18, '1-7', 1234567, 'BF49F267', 'map/gui/wagons_basic_set.png',
#		'F671771F', 0.6, 0, 0, 170, 45, 23, '-1', '{"Cash": 1.0}', 0, NULL, NULL)""")

	("""INSERT INTO data("index", name, source, vanilla, id, cid,
		vehicle_type, track, weight_full, weight_empty, epoch, eras, icon,
		icon_texture, icon_color, length_b, length_head, length_tail, power,
		max_speed, max_speed_reverse, raw_cost, cost, capacity, raw_effect,
		runway_length_needed) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
		?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""")
	print(prepare_query())



# QSQLITE_ENABLE_REGEXP
class TableModel(QSqlRelationalTableModel):
	db: QSqlDatabase
	def __init__(self, parent: QObject, data: list[Row]):
		self.db = QSqlDatabase.addDatabase("QSQLITE")
		self.db.setDatabaseName(":memory:")
		self.db.setConnectOptions("QSQLITE_ENABLE_REGEXP")
		if not self.db.open():
			raise ValueError(self.db.lastError())
		super().__init__(parent, self.db)
		createRelationalTables(self.db)
		self.initializeModel()
		self.insert_data(data)
		self.select()

	def initializeModel(self):
		self.setTable("data")
		self.setEditStrategy(QSqlRelationalTableModel.OnManualSubmit)
		self.setHeaderData(0, Qt.Orientation.Horizontal, QObject().tr("ID"))

		#model.setHeaderData(1, Qt.Orientation.Horizontal, QObject().tr("Name"))
		#model.setHeaderData(2, Qt.Orientation.Horizontal, QObject().tr("City"))
		#model.setHeaderData(3, Qt.Orientation.Horizontal, QObject().tr("Country"))

	def insert_data(self, data: list[Row]):
		query = QSqlQuery(self.db)
		def prepare(*args):
			if not query.prepare(*args):
				raise ValueError(query.lastError())
		prepare(prepare_query())
		check = lambda *args: check_exec(query, *args)
		for r in data:
			#print(r)
			bind_query(query, r)
			#print(query.executedQuery())
			check()
	def update_adj_cost(self):
		query = QSqlQuery(self.db)
		check = lambda *args: check_exec(query, *args)
		numAffected = 0
		changed = []

		check("SELECT name,value FROM budget")
		while query.next():
			rec = query.record()
			if rec.value(1) != token_supply[rec.value(0)]:
				rec.setValue(1, token_supply[rec.value(0)])
				changed.append(rec.value(0))


		#check(f"INSERT INTO budget VALUES('Cash', {token_supply['Cash']})")
		#check(f"INSERT INTO budget VALUES('Coal', {token_supply['Coal']})")
		#check(f"INSERT INTO budget VALUES('Diesel', {token_supply['Diesel']})")
		#check(f"INSERT INTO budget VALUES('Electric', {token_supply['Electric']})")
		if changed:
			where = ' AND '.join((f"{c} != 0" for c in changed))
			check(f"UPDATE data SET (adjcost,TP_adjcost)=() WHERE {where}")
			self.select()

	def show_data(self):
		q = QSqlQuery("SELECT * FROM data")
		rec = q.record()
		while q.next():
			for c in range(rec.count()):
				print(f'{q.value(c)}\t', end='')
			print()



def delta_ms(a,b):
	return (b-a)/1000000
def show_times(times):
	for a,b in itertools.pairwise(times):
		print(f'{a[0]}: {delta_ms(a[1],b[1])}ms')
class Proxy(QSortFilterProxyModel):
	pass

if __name__ == "__main__":
	times = []
	times.append(("start", time.monotonic_ns()))
	app = QApplication(sys.argv)
	args, files, vfiles = handle_cli(True)
	times.append(("io.find", time.monotonic_ns()))
	files = find_files(args.files, args.path)
	vfiles = find_files(args.vanilla, args.vanilla_dir)
	times.append(("io.read", time.monotonic_ns()))
	#global icon_map
	data,icon_map = read_files(files, vfiles)
	times.append(("create table", time.monotonic_ns()))
	model = TableModel(None, data)
	times.append(("window", time.monotonic_ns()))
	title = "Relational Table Model"
	window = createView(title, model)
	window.resize(600, 200)
	window.show()
	times.append(("show", time.monotonic_ns()))
	#model.show_data()
	times.append(("end", time.monotonic_ns()))
	show_times(times)

	sys.exit(app.exec())
