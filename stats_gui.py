# This Python file uses the following encoding: utf-8
import functools
from pathlib import Path
import sys
import time

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget,
	QTableWidgetItem, QHeaderView, QLabel)
from PySide6.QtCore import Slot, Qt, QPoint, QSize
from PySide6.QtGui import QColor, QBrush, QPixmap, QImage
from ui_mainwindow import Ui_MainWindow

from mashinky_stats import (Row, handle_cli, read_files,
	token_supply, adj_costs, rnd)
import constants as C
import cmap

pls_help_bug = []

def translate_header(l):
	return Row.__dict__.get(l).tbl if l in Row.__dict__ else l

def fmt_cell(field, contents):
	if field == 'index':
		return ('     '+str(contents))[-5:]
	else:
		return str(rnd(contents))

def log_timer(oself=None, print_args=True, quiet=False):
	#print(f"log_timer({oself})")
	def decorator(func):
		#print(f"log_timer({oself})({func}) {type(func)}")
		def select_widget(args):
			if oself:
				return oself.timer_widget
			else:
				return args[0].timer_widget
		@functools.wraps(func)
		def impl2(*args, **kwargs):
			#return func(*args, **kwargs)
			#print(repr(type(args[0])))
			start = time.monotonic_ns()
			ret = func(*args, **kwargs)
			end = time.monotonic_ns()
			delta_ms = (end-start)/1000000
			#print(select_widget(args))
			select_widget(args).setText(f"{func.__name__}: {delta_ms}ms")
			if quiet:
				return ret
			if print_args:
				def s(x):
					if type(x) is Row:
						return "<Row>"
					elif type(x) is list:
						return "<list>"
					elif type(x) is MainWindow:
						return "self"
					elif isinstance(x, QWidget):
						return x.objectName()
					else:
						return str(x)
				args_s = ', '.join([s(x) for x in args])
				print(f"{func.__name__}({args_s}) took {delta_ms}ms")
			else:
				print(f"{func.__name__}() took {delta_ms}ms")
			return ret
		return impl2
	if callable(oself):
		raise ValueError()
	return decorator

currencies = ['cash', 'coal', 'diesel', 'electric', 'adjcost',]
map_curs = lambda pfx: [pfx + cur for cur in currencies]
red = QColor.fromRgb(255, 224, 224)

icon_map = {}

class MainWindow(QMainWindow):
	engine_labels = [
		'name', 'max_speed', 'max_speed_mph', 'power', 'traction', 'towage', 'weight',
		'length', 'eras', 'throughput', 'pwt_full', 'pwt_empty',
		'tow_per_length', 'power_per_length',
		]+map_curs('TP_')+currencies+[
		'CD6', 'CD8', 'era', 'id', 'source', 'vanilla', 'index'
	]
	wagon_labels = [
		'name', 'ctype', 'capacity', 'weight_empty', 'weight_full', 'length', 'eras',
		'bonus', 'cargo_per_length', 'cargo_per_wt', 'compound_efficiency',
		'density', 'profit', 'profit_per_length', 'profit_per_wt',
		'compound_profitability', 'wt_per_cargo', 'era', 'id', 'cid', 'source',
		'power', 'vanilla', 'index'
	]
	vehicle_labels = [
		'name', 'ctype', 'capacity', 'max_speed', 'max_speed_mph', 'power',
		'weight_empty', 'weight_full', 'length', 'eras', 'bonus',
		'pwt_full', 'pwt_empty', 'throughput', 'cargo_throughput',
		'cargo_per_length', 'profit', 'profit_per_length', 'cargo_unit_wt',
		]+map_curs('TP_')+currencies+map_curs('TPc_')+map_curs('TPp_')+[
		'era', 'id', 'cid', 'source', 'vanilla', 'index'
	]
	aircraft_labels = vehicle_labels.copy()
	all_labels = Row().keys()
	disp = {"unit": 0, "cmap": "None", "cmap_inv": False}
	speed_units = (['max_speed', 'max_speed_reverse'], ['max_speed_mph', 'max_speed_reverse_mph'])
	data = []
	tables = []
	ui = Ui_MainWindow()
	populated = False
	timer_widget = None
	cmaps = {}
	active_cmap = None
	cmap_img = None

	@log_timer()
	def handle_cli(self):
		self.args, self.files, self.vfiles = handle_cli(True)

	def g_cur_idxs(self):
		def scan(labels):
			ret = []
			for i,l in enumerate(labels):
				if any((cur in l for cur in currencies)):
					ret.append(i)
			return ret
		return [scan(labels) for tbl, labels, data in self.tables]

	@log_timer()
	def setupUi(self):
		self.ui.setupUi(self)


	def format_files_to_text(self, dirs: list[Path], files: list[Path]) -> tuple[str, str]:
		vars = {Path('.'): Path.cwd()}
		def shortest(roots: dict[Path, Path], path: Path) -> Path:
			ret = path
			for id,root in roots.items():
				try:
					rp = id/path.relative_to(root)
					if len(str(rp)) < len(str(ret)):
						ret = rp
				except ValueError:
					pass
			return ret

		if len(dirs) == 1:
			root = dirs[0]
			vars |= {Path('$m'): Path(root)}
		else:
			vars |= {Path(f'$m{i}'): Path(p) for i,p in enumerate(dirs)}
		return (" ".join((f'{id}={p}' for id,p in vars.items() if id != Path('.'))),
			" ".join((str(shortest(vars, p)) for p in files)))

	@log_timer()
	def __init__(self, argv):
		super(MainWindow, self).__init__()
		self.timer_widget = QLabel()

		self.handle_cli()
		self.setupUi()
		self.load_cmaps()

		self.statusBar().addPermanentWidget(self.timer_widget)

		self.ui.amt_cash.setValue(token_supply[C.CASH])
		self.ui.amt_coal.setValue(token_supply[C.COAL])
		self.ui.amt_diesel.setValue(token_supply[C.DIESEL])
		self.ui.amt_electric.setValue(token_supply[C.ELECTRIC])

		moddirs, modfiles = self.format_files_to_text(self.args.path, self.files)
		self.ui.txt_moddir.setText(moddirs)
		self.ui.txt_modfiles.setText(" ".join(self.args.files))
		vdirs, vfiles = self.format_files_to_text(self.args.vanilla_dir, self.vfiles)
		self.ui.txt_vdir.setText(vdirs)
		self.ui.txt_vfiles.setText(" ".join(self.args.vanilla))
		print(f"loaded {len(self.files)}+{len(self.vfiles)} files")

		self.ui.txt_found_modfiles.setPlainText(modfiles)
		self.ui.txt_found_vfiles.setPlainText(vfiles)

		self.update_data()
		self.cur_idxs = self.g_cur_idxs()
		self.populate()
		self.dirty = [False]*len(self.tables)
		#print(self.all_labels)

	@log_timer()
	def update_data(self):
		global icon_map
		self.data,icon_map = read_files(self.files, self.vfiles)
		#print(repr(icon_map))
		print(len(icon_map), "tcoords")
		filt = lambda f: [r.index for r in self.data if f(r)]

		self.tables = [
			(self.ui.tbl_engines, self.engine_labels, filt(Row.is_engine)),
			(self.ui.tbl_wagons, self.wagon_labels, filt(Row.is_wagon)),
			(self.ui.tbl_vehicles, self.vehicle_labels, filt(Row.is_vehicle)),
			(self.ui.tbl_aircraft, self.aircraft_labels, filt(Row.is_aircraft)),
			#(self.ui.tbl_all, self.all_labels, list(range(min(len(self.data), 250)))),
			(self.ui.tbl_all, self.all_labels, list(range(len(self.data)))),
		]

	@log_timer()
	def populate(self):
		for tbl, labels, d in self.tables:
			self.populate_table(tbl, labels, d)
			h = tbl.horizontalHeader()
			h.setSectionsMovable(True)
			h.setSortIndicatorClearable(True)
			h.setResizeContentsPrecision(8)
			h.resizeSections(QHeaderView.ResizeMode.ResizeToContents)
			tbl.setSortingEnabled(True)
			tbl.cellClicked.connect(self.tbl_click(tbl))
			#self.reset_labels_for(tbl)
		self.update_units()
		self.update_curs()
		self.populated = True

		sizes = [(tbl.columnCount(), tbl.rowCount()) for tbl, l, d in self.tables]

		self.statusBar().showMessage(
			", ".join([f"{h}*{w}={w*h}" for (w, h) in sizes])
			+ " cells, " + str(sum((w*h for w, h in sizes))) + " total")

	@log_timer()
	def populate_table(self, tbl, labels, d):
		tbl.setColumnCount(len(labels))
		l2 = [translate_header(l) for l in labels]
		tbl.setHorizontalHeaderLabels(l2)
		tbl.setRowCount(len(d))
		tbl.setVerticalHeaderLabels([
			self.data[row].name for row in d])
		vh = tbl.verticalHeader()
		for r, i in enumerate(d):
			for c, f in enumerate(labels):
				d = self.data[i][f]
				txt = fmt_cell(f, d)
				item = QTableWidgetItem(txt)
				if len(txt) > 10:
					item.setToolTip(txt)
				tbl.setItem(r, c, item)
				pls_help_bug.append(None)
				vh.resizeSection(r, 22)
				pls_help_bug.append(None)
		#vh.setResizeContentsPrecision(1)
		#vh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
		h = tbl.horizontalHeader()
		h.sortIndicatorChanged.connect(self.reset_labels(tbl))
		tbl.hideColumn(0)
		tbl.sortItems(0, Qt.SortOrder.AscendingOrder)

	@Slot()
	def update_units(self):
		unhidden_fields = []
		hidden_fields = []
		for i,fs in enumerate(self.speed_units):
			if i == self.disp['unit']:
				unhidden_fields += fs
			else:
				hidden_fields += fs
		for tbl, labels, d in self.tables:
			for i,l in enumerate(labels):
				if l in unhidden_fields:
					tbl.showColumn(i)
				elif l in hidden_fields:
					tbl.hideColumn(i)

	def update_curs(self):
		adj = adj_costs({cur: 1 for cur in C.CURRENCIES})
		for cur in range(4):
			self.ui.__getattribute__(f"lbl_adj_{currencies[cur]}").setText(
				str(rnd(adj[cur],100)))
		self.dirty = [True]*len(self.tables)

	@Slot()
	@log_timer()
	def update_views(self):
		if not self.populated:
			return
		self.update_curs()
		counts = []
		for idx in range(len(self.tables)):
			self.dirty[idx] = False
			tbl, labels, d = self.tables[idx]
			idx_c = -1
			for c,l in enumerate(labels):
				if l == 'index':
					idx_c = c
			sort = tbl.isSortingEnabled()
			tbl.setSortingEnabled(False)
			count = 0
			for r in range(tbl.rowCount()):
				for c in self.cur_idxs[idx]:
					f = labels[c]
					key = int(tbl.item(r,idx_c).text())
					item = tbl.item(r,c)
					new = fmt_cell(f, self.data[key][f])
					old = item.text()
					if new != old:
						#print(f"{tbl.objectName()}item({r},{c}) '{new}' != '{old}'")
						item.setText(new)
						item.setBackground(red)
						count = count + 1
					elif item.background() != QBrush():
						item.setBackground(QBrush())
					pls_help_bug.append(None)
			counts.append(count)
			if (sort):
				tbl.setSortingEnabled(True)
				self.reset_labels_for(tbl)
		self.statusBar().showMessage("Updated " + ", ".join(
			(str(c) for c in counts)) + " items")

	@Slot(int)
	def update_table(self, idx):
		if idx >= len(self.tables) or not self.dirty[idx]:
			return
		self.update_views()
		self.dirty[idx] = False

	def reset_labels(self, tbl):
		@Slot(int, Qt.SortOrder)
		def reset_labels_impl(v, o):
			#if self.populated:
				#print(f"reset({v}, {o})")
			if v == -1:
				tbl.sortItems(0, Qt.SortOrder.AscendingOrder)
			tbl.sortItems(tbl.horizontalHeader().sortIndicatorSection(), o)
			self.reset_labels_for(tbl)
		return reset_labels_impl

	def reset_labels_for(self, tbl):
		van_idx = -1
		name_idx = -1
		for c in range(tbl.columnCount()):
			if tbl.horizontalHeaderItem(c).text() == C.VANILLA:
				van_idx = c
			if tbl.horizontalHeaderItem(c).text() == C.NAME:
				name_idx = c
		tbl.hideColumn(van_idx)
		for r in range(tbl.rowCount()):
			#print(f"set v{r} from {tbl.verticalHeaderItem(r).text()} to {tbl.item(r,0).text()}")
			l = tbl.verticalHeaderItem(r)
			l.setText(tbl.item(r,name_idx).text())
			if tbl.item(r,van_idx).text() == "True":
				l.setBackground(QColor.fromHslF(0.542, .8, .8, .6))
			else:
				l.setBackground(QColor.fromHslF(0.333, .7, .85, .6))

	def tbl_click(self, tbl):
		@Slot(int, int)
		def impl(cr, cc):
			print(f"{tbl.objectName()}.tbl_click({cr},{cc})")
			for r in range(tbl.rowCount()):
				for c in range(tbl.columnCount()):
					pls_help_bug.append(None)
					if r == cr:
						tbl.item(r, c).setBackground(QColor.fromString("#eee"))
					else:
						tbl.item(r, c).setBackground(QBrush())
		return impl

	@Slot(QPoint)
	def tbl_context_menu(self, point):
		print(f"context menu for {point}")

	@Slot()
	@log_timer()
	def load_cmaps(self):
		self.populated = False
		self.cmaps = {}
		selected = self.disp["cmap"]
		for cm in self.args.cmap:
			self.cmaps |= cmap.from_file(cm)
		sel = self.ui.sel_cmap
		sel.clear()
		sel.addItem("None")
		sel.addItems(self.cmaps.keys())
		#print(f"current cmap {selected}")
		self.populated = True
		sel.setCurrentText(selected)
		self.update_cmap()

	@log_timer()
	def update_cmap(self):
		if not self.populated:
			return
		if self.disp["cmap"] == "None":
			#print("no cmap")
			self.ui.sel_cmap_inv.setEnabled(False)
			self.active_cmap = None
		else:
			#print(f"current cmap {self.disp['cmap']}")
			try:
				self.ui.sel_cmap_inv.setEnabled(True)
				if self.disp["cmap_inv"]:
					#print("inverted")
					self.active_cmap = reversed(self.cmaps[self.disp["cmap"]])
				else:
					self.active_cmap = self.cmaps[self.disp["cmap"]]
			except KeyError:
				print(f"Resetting cmap because {self.disp['cmap']} doesn't exist")
				self.ui.sel_cmap.setCurrentText("None")
				# the docs say the signal is supposed to be emitted automatically
				# but it doesn't seem to be
				return self.set_disp_cmap("None")

		#print(self.disp)
		#print(self.active_cmap)
		self.update_vis_cmap()

		# iterate tables?
		# or maybe update a stylesheet

	#@log_timer()
	def update_vis_cmap(self):
		label = self.ui.vis_cmap
		rect = label.size()
		borders = 2*label.frameWidth() + 2*label.margin()
		width = (rect.width() - borders)
		print(f"resize: {rect};{width}")
		if self.active_cmap is None:
			label.clear()
			return
		#
		#if not self.cmap_img:
		self.cmap_img = QImage(width, 1, QImage.Format.Format_RGB32)
		self.cmap_img.fill(QColor.fromRgbF(0xee,0xfe,0xef))
#		elif type(self.cmap_img) is QPixmap:
#			self.cmap_img = self.cmap_img.copy(0, 0, width, 1)
#			self.cmap_img.fill(QColor.fromRgbF(0xee,0xfe,0xef))
		line = self.cmap_img.scanLine(0)
		for i in range(width):
			c = self.active_cmap.interpolate(i/(width-1))
			line[(i*4):(i*4)+3] = bytearray((c.blue(), c.green(), c.red()))
			#self.cmap_img.setPixelColor(i,0,c)
		self.cmap_pix = QPixmap.fromImage(self.cmap_img)
		label.setPixmap(self.cmap_pix)
		label.setMinimumSize(1,label.height())

	def resizeEvent(self, event):
		#print(f"resizeEvent: {event.oldSize()}->{event.size()}")
		if event.size().width() != event.oldSize().width() and self.active_cmap:
			self.update_vis_cmap()



	@Slot()
	def open(self):
		print("open")

	@Slot(int)
	def set_cash(self, val):
		if not self.populated:
			return
		token_supply[C.CASH] = val
		self.update_curs()
	@Slot(int)
	def set_coal(self, val):
		if not self.populated:
			return
		token_supply[C.COAL] = val
		self.update_curs()
	@Slot(int)
	def set_diesel(self, val):
		if not self.populated:
			return
		token_supply[C.DIESEL] = val
		self.update_curs()
	@Slot(int)
	def set_electric(self, val):
		if not self.populated:
			return
		token_supply[C.ELECTRIC] = val
		self.update_curs()
	@Slot(int)
	def set_disp_unit(self, val):
		if not self.populated:
			return
		self.disp["unit"] = val
		self.update_units()
	@Slot(str)
	def set_disp_cmap(self, val):
		#print(f"set_disp_cmap(self, {repr(val)}")
		if not self.populated:
			return
		self.disp["cmap"] = val
		self.update_cmap()
	@Slot(int)
	def set_disp_cmap_inv(self, val):
		if not self.populated:
			return
		self.disp["cmap_inv"] = bool(val)
		self.update_cmap()


if __name__ == "__main__":
	app = QApplication(sys.argv)

	window = MainWindow(sys.argv)
	window.show()
	#window.update_views()

	sys.exit(app.exec())

# Todo:
# Add cmaps and highlighting
# I haven't quite decided if I'm going to do a custom model/view thing or use a
#	QSqlTableModel with an in-memory sqlite3 db
# Add search
# Add column hiding
# Probably replace my custom field with dataclasses.field and use its metadata
