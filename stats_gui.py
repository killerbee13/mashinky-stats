# This Python file uses the following encoding: utf-8
from collections import defaultdict
import functools
from pathlib import Path
import sys
import time

#import traceback
#import numpy as np

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget,
	QTableWidgetItem, QHeaderView, QLabel, QFrame)
from PySide6.QtCore import Slot, Qt, QPoint
from PySide6.QtGui import QColor, QBrush, QPixmap, QImage, QCursor
from ui_mainwindow import Ui_MainWindow

import constants as C
from mashinky_stats import handle_cli, find_files, read_files
from TableModel import Disp, Row, token_supply, adj_costs, rnd
import cmap

pls_help_bug = []

def translate_header(l):
	return Row.__dict__.get(l).tbl if l in Row.__dict__ else l

def fmt_cell(field, contents):
	if field == 'index':
		return ('     '+str(contents))[-5:]
	else:
		return str(rnd(contents))

log_timer_nest_level = -1
def log_timer(oself=None, print_args=True, quiet=False):
	#print(f"log_timer({oself})")
	def decorator(func):
		#print(f"log_timer({oself})({func}) {type(func)}")
		def select_widget(args):
			if oself:
				return oself.timer_widget
			else:
				return args[0].timer_widget
		def pfx():
			return f"{time.strftime('%H:%M:%S')}:{'.'*log_timer_nest_level}"
		@functools.wraps(func)
		def impl2(*args, **kwargs):
			#return func(*args, **kwargs)
			#print(repr(type(args[0])))
			start = time.monotonic_ns()
			global log_timer_nest_level
			log_timer_nest_level = log_timer_nest_level + 1
			if not quiet:
				print(pfx()+f">{func.__name__}")
			ret = func(*args, **kwargs)
			end = time.monotonic_ns()
			delta_ms = (end-start)/1000000
			args_s = ""
			if print_args:
				def s(x):
					if type(x) is Row:
						return "<Row>"
					elif type(x) is list:
						return "<list>"
					elif type(x) is MainWindow:
						return "window"
					elif isinstance(x, QWidget):
						return x.objectName()
					else:
						return str(x)
				args_s = '('+', '.join([s(x) for x in args[(1 if type(args[0]) is MainWindow else 0):]])+')'
			#print(select_widget(args))
			if delta_ms > 10:
				select_widget(args).setText(f"{func.__name__}{args_s}: {delta_ms}ms"
					f" | {len(pls_help_bug)} bug prayers")
			if quiet:
				return ret
			print(pfx()+f"<{func.__name__}{args_s} took {delta_ms}ms"
				f" [{time.thread_time_ns()/1000000}ms]")
			log_timer_nest_level = log_timer_nest_level - 1
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
		'length', 'eras', 'throughput', 'pwt_loaded', 'pwt_empty',
		'tow_per_length', 'power_per_length',
		]+map_curs('TP_')+currencies+[
		'track', 'CD6', 'CD8', 'era', 'id', 'source', 'vanilla', 'index'
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
		'pwt_full', 'pwt_empty', 'cargo_throughput',
		'cargo_per_length', 'profit', 'profit_per_length', 'cargo_unit_wt',
		]+currencies+map_curs('TPc_')+map_curs('TPp_')+[
		'era', 'id', 'cid', 'source', 'vanilla', 'index'
	]
	aircraft_labels = vehicle_labels.copy()
	all_labels = Row().keys()
	disp = {"unit": 0, "cmap": "None", "cmap_inv": False}
	speed_units = (['max_speed', 'max_speed_reverse'], ['max_speed_mph', 'max_speed_reverse_mph'])
	data = []
	tables = (None,None,None,None,None)
	ui = Ui_MainWindow()
	app: QApplication
	populated = [False]*6
	dirty = [False]*5
	timer_widget = None
	cmaps = {}
	active_cmap = None
	cmap_img = None
	table_last_cmap = [None]*len(tables)
	tab = 0
	prefs_tab = 5

	@log_timer()
	def handle_cli(self):
		self.args, self.files, self.vfiles = handle_cli(True)

	def g_cur_idxs(self):
		def scan(labels):
			ret = []
			for i,l in enumerate(labels):
				if 'adj' in l:
					ret.append(i)
			return ret
		return [scan(labels) for tbl, labels, data in self.tables]

	@log_timer()
	def setupUi(self):
		self.ui.setupUi(self)
		self.tab = self.ui.tabWidget.currentIndex()


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
	def __init__(self, app, argv):
		super(MainWindow, self).__init__()
		self.app = app
		self.cmap_widget = QLabel(self)
		self.cmap_widget.setObjectName('cmap_widget')
		self.timer_widget = QLabel(self)
		self.timer_widget.setObjectName('timer_widget')

		self.handle_cli()
		self.setupUi()
		self.load_cmaps()
		if self.args.color:
			if self.args.color in self.cmaps:
				self.ui.sel_cmap.setCurrentText(self.args.color)
				#self.set_disp_cmap(self.args.color)
			else:
				color = cmap.reverse_name(self.args.color)
				if color in self.cmaps:
					self.ui.sel_cmap.setCurrentText(color)
					self.ui.sel_cmap_inv.setChecked(True)
					#self.set_disp_cmap(color)
		self.update_cmap()

		self.statusBar().addPermanentWidget(self.timer_widget)
		self.statusBar().addPermanentWidget(self.cmap_widget)

		self.ui.amt_cash.setValue(token_supply[C.CASH])
		self.ui.amt_coal.setValue(token_supply[C.COAL])
		self.ui.amt_diesel.setValue(token_supply[C.DIESEL])
		self.ui.amt_electric.setValue(token_supply[C.ELECTRIC])

		def walkchildren(widget, parent):
			for child in widget.children():
				#name = (child.objectName() or hex(id(child)))
				#print(f"{parent}.{name} {child}")
				if isinstance(child, QFrame):
					child.setFrameShape(QFrame.Shape.Panel)
					child.setFrameShadow(QFrame.Shadow.Sunken)
				#walkchildren(child, parent + '.' + name)
		walkchildren(self.statusBar(), 'statusBar')

		self.read_data(reload=False)
		self.cur_idxs = self.g_cur_idxs()
		self.populated[self.prefs_tab] = True
		for idx, (tbl, l, d) in enumerate(self.tables):
			tbl.cellClicked.connect(self.tbl_click(idx))

	@Slot()
	@log_timer()
	def read_data(self, reload=True):
		if reload:
			self.files = find_files(self.args.files, self.args.path)
			self.vfiles = find_files(self.args.vanilla, self.args.vanilla_dir)

		moddirs, modfiles = self.format_files_to_text(self.args.path, self.files)
		self.ui.txt_moddir.setText(moddirs)
		self.ui.txt_modfiles.setText(" ".join(self.args.files))
		vdirs, vfiles = self.format_files_to_text(self.args.vanilla_dir, self.vfiles)
		self.ui.txt_vdir.setText(vdirs)
		self.ui.txt_vfiles.setText(" ".join(self.args.vanilla))
		self.ui.txt_found_modfiles.setPlainText(modfiles)
		self.ui.txt_found_vfiles.setPlainText(vfiles)
		print(f"loaded {len(self.files)}+{len(self.vfiles)} files")

		#self.populated = False
		self.update_data()
		self.populate()
		# Needed because the tables will have been already sorted, so
		# sortIndicatorChanged may not be emitted
		if reload:
			for idx in range(len(self.tables)):
				self.reset_labels_for(idx)

	@log_timer()
	def do_read_files(self):
		global icon_map
		self.data,icon_map = read_files(self.files, self.vfiles)


	@log_timer()
	def update_data(self):
		self.do_read_files()
		self.setWindowTitle(f"Mashinky Stats Viewer - "
			f"{len(self.vfiles)}v+{len(self.files)}m files, "
			f"{len(self.data)} entities, {len(icon_map)} tcoords")
		#print(repr(icon_map))
		print(len(icon_map), "tcoords")
		filt = lambda f: [r.index for r in self.data if f(r)]

		self.tables = (
			(self.ui.tbl_engines, self.engine_labels, filt(Row.is_engine)),
			(self.ui.tbl_wagons, self.wagon_labels, filt(Row.is_wagon)),
			(self.ui.tbl_vehicles, self.vehicle_labels, filt(Row.is_vehicle)),
			(self.ui.tbl_aircraft, self.aircraft_labels, filt(Row.is_aircraft)),
			#(self.ui.tbl_all, self.all_labels, list(range(min(len(self.data), 250)))),
			(self.ui.tbl_all, self.all_labels, list(range(len(self.data)))),
		)
		for i in range(len(self.tables)):
			self.populated[i] = False

	@log_timer()
	def populate(self):
		#for idx, (tbl, labels, d) in enumerate(self.tables):
			#print(d)
			#self.populate_table(idx)
		self.populate_table(self.tab)
		self.update_units()
		self.update_curs()
		self.dirty = [False]*len(self.tables)

		sizes = [(tbl.columnCount(), tbl.rowCount()) for tbl, l, d in self.tables]

		self.statusBar().showMessage(
			", ".join([f"{h}*{w}={w*h}" for (w, h) in sizes])
			+ " cells, " + str(sum((w*h for w, h in sizes))) + " total")

	@log_timer()
	def populate_table(self, idx):
		if idx == self.prefs_tab:
			return
		tbl, labels, d = self.tables[idx]
		tbl.clear()
		tbl.setSortingEnabled(False)
		tbl.setColumnCount(len(labels))
		l2 = [translate_header(l) for l in labels]
		tbl.setHorizontalHeaderLabels(l2)
		tbl.setRowCount(len(d))
		tbl.setVerticalHeaderLabels([
			self.data[row].name for row in d])
		vh = tbl.verticalHeader()
		for c, f in enumerate(labels):
			#print(d)
			params = self.params(d, f, tbl is not self.ui.tbl_engines)
			for r, i in enumerate(d):
				dat = self.data[i]
				txt = fmt_cell(f, dat[f])
				item = QTableWidgetItem(txt)
				pls_help_bug.append(None)
				if len(txt) > 10:
					item.setToolTip(txt)
				self.color(dat, item, params, tbl, f)
				tbl.setItem(r, c, item)
				pls_help_bug.append(None)
				vh.resizeSection(r, 22)
				pls_help_bug.append(None)
		#vh.setResizeContentsPrecision(1)
		#vh.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
		h = tbl.horizontalHeader()
		h.sortIndicatorChanged.connect(self.reset_labels(idx))
		tbl.hideColumn(0)
		tbl.sortItems(0, Qt.SortOrder.AscendingOrder)
		h = tbl.horizontalHeader()
		h.setSectionsMovable(True)
		h.setSortIndicatorClearable(True)
		h.setResizeContentsPrecision(8)
		h.resizeSections(QHeaderView.ResizeMode.ResizeToContents)
		tbl.setSortingEnabled(True)
		#self.reset_labels_for(idx)
		self.table_last_cmap[idx] = self.active_cmap
		self.populated[idx] = True

	@log_timer()
	def update_colors(self, idx):
		tbl, labels, d = self.tables[idx]
		idx_c = -1
		for c,l in enumerate(labels):
			if l == 'index':
				idx_c = c
		for c, f in enumerate(labels):
			params = self.params(d, f, idx != 0)
			for r in range(tbl.rowCount()):
				key = int(tbl.item(r,idx_c).text())
				pls_help_bug.append(None)
				self.color(self.data[key], tbl.item(r,c), params, tbl, f) or tbl.item(r,c).setBackground(QBrush())
		self.table_last_cmap[idx] = self.active_cmap

	#@log_timer()
	def params(self, d, f, do_bin):
		field = Row.__dict__[f]
		if field.disp == Disp.Positive:
			def minmax(l):
				return min(l), max(l)
		elif field.disp == Disp.Negative:
			def minmax(l):
				return max(l), min(l)
		else:
			return
		#print(d)
		if do_bin:
			bins = defaultdict(list)
			for row in d:
				try:
					v = float(self.data[row][f])
					if f is not None:
						bins[self.data[row].cid].append(v)
				except TypeError:
					pass
				except KeyError:
					pass
				except ValueError:
					pass
			return {k: minmax(b) for k,b in bins.items()}
		else:
			l = []
			for row in d:
				try:
					v = float(self.data[row][f])
					if f is not None:
						l.append(v)
				except TypeError:
					pass
				except KeyError:
					pass
				except ValueError:
					pass
			return {None: minmax(l)}

	def color(self, dat, item, params, tbl, f):
		"""Set the background color on item from the current cmap.
		Return value is true when the color of item was updated."""
		if self.active_cmap and dat[f] != '':
			d = dat[f]
			bin = dat.cid if tbl is not self.ui.tbl_engines else None
			t = -1
			if params:
				try:
					t = cmap.inv_lerp(params[bin][0], params[bin][1], float(d))
				except ValueError:
					print(f"color VE {f} {repr(d)} {repr(params)}[{repr(bin)}]={repr(params[bin])}")
					return False
				except KeyError:
					print(f"color KE {f} {repr(d)} {repr(params)}[{repr(bin)}]")
					#item.setBackground(QColor.fromRgbF(1,0,0,1))
					return False
			elif Row.__dict__[f].disp == Disp.Parity:
				if int(d) % 2 == 1:
					t = 1/3
				else:
					t = 2/3
			elif Row.__dict__[f].disp == Disp.Null:
				return False
			else:
				raise ValueError(f"Unknown disposition? {f} {repr(d)} {repr(bin)} {Row.__dict__[f].disp}")
			c = self.active_cmap.interpolate(t)
			c.setAlphaF(.8)
			item.setBackground(c)
			pls_help_bug.append(None)
			return True
		else:
			return False


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
		for cur in range(len(currencies)-1):
			self.ui.__getattribute__(f"lbl_adj_{currencies[cur]}").setText(
				str(rnd(adj[cur],100)))
		self.dirty = [True]*len(self.tables)

	@log_timer()
	def update_column(self, count, idx, c, idx_c):
		tbl, labels, d = self.tables[idx]
		params = self.params(d, labels[c], idx != 0)
		for r in range(tbl.rowCount()):
			f = labels[c]
			key = int(tbl.item(r,idx_c).text())
			item = tbl.item(r,c)
			dat = self.data[key]
			new = fmt_cell(f, dat[f])
			old = item.text()
			if new != old:
				#print(f"{tbl.objectName()}item({r},{c}) '{new}' != '{old}'")
				item.setText(new)
				# change to setFont to set underline or italic
				item.setBackground(red)
				pls_help_bug.append(None)
				self.color(dat, item, params, tbl, f)
				count = count + 1
			elif item.background() != QBrush():
				#item.setBackground(QBrush())
				self.color(dat, item, params, tbl, f)
			pls_help_bug.append(None)
		return count


	@Slot()
	@log_timer()
	def update_views(self, idx):
		if not self.populated[self.prefs_tab]:
			return False
		self.update_curs()
		counts = []
		#for idx in range(len(self.tables)):
		self.dirty[idx] = False
		tbl, labels, d = self.tables[idx]
		idx_c = -1
		for c,l in enumerate(labels):
			if l == 'index':
				idx_c = c
		sort = tbl.isSortingEnabled()
		tbl.setSortingEnabled(False)
		count = 0
		for c in self.cur_idxs[idx]:
			count = self.update_column(count, idx, c, idx_c)
		counts.append(count)
		if (sort):
			tbl.setSortingEnabled(True)
		self.reset_labels_for(idx)
		if sum(counts):
			self.statusBar().showMessage("Updated " + ", ".join(
				(str(c) for c in counts)) + " items")
		return True

	@Slot(int)
	@log_timer()
	def update_table(self, idx):
		self.tab = idx
		if idx < len(self.tables):
			self.app.setOverrideCursor(QCursor(Qt.WaitCursor))
			try:
				if not self.populated[idx]:
					self.populate_table(idx)
					self.reset_labels_for(idx)
				if self.dirty[idx]:
					self.dirty[idx] = not self.update_views(idx)
				if self.table_last_cmap[idx] is not self.active_cmap:
					self.update_colors(idx)
			finally:
				self.app.restoreOverrideCursor()

	def reset_labels(self, idx):
		@Slot(int, Qt.SortOrder)
		def reset_labels_impl(v, o):
			#if self.populated[self.prefs_tab]:
				#print(f"reset({v}, {o})")
			tbl = self.tables[idx][0]
			if v == -1:
				tbl.sortItems(0, Qt.SortOrder.AscendingOrder)
			tbl.sortItems(tbl.horizontalHeader().sortIndicatorSection(), o)
			self.reset_labels_for(idx)
		return reset_labels_impl

	@log_timer()
	def reset_labels_for(self, idx):
		tbl, labels, d = self.tables[idx]
		van_idx = -1
		name_idx = -1
		for c in range(tbl.columnCount()):
			if tbl.horizontalHeaderItem(c).text() == C.VANILLA:
				van_idx = c
			if tbl.horizontalHeaderItem(c).text() == C.NAME:
				name_idx = c
		tbl.hideColumn(van_idx)
		for r in range(tbl.rowCount()):
			#print(f"set v{r} from {tbl.verticalHeaderItem(r).text()} to [{r}][0] {tbl.item(r,0).text()}")
			l = tbl.verticalHeaderItem(r)
			l.setText(tbl.item(r,name_idx).text())
			if tbl.item(r,van_idx).text() == "True":
				l.setBackground(QColor.fromHslF(0.542, .8, .8, .6))
			else:
				l.setBackground(QColor.fromHslF(0.333, .7, .85, .6))
			pls_help_bug.append(None)

	def tbl_click(self, idx):
		@Slot(int, int)
		def impl(cr, cc):
			tbl, labels, d = self.tables[idx]
			print(f"{tbl.objectName()}.tbl_click({cr},{cc})")
			return
#			for r in range(tbl.rowCount()):
#				for c in range(tbl.columnCount()):
#					pls_help_bug.append(None)
#					if r == cr:
#						tbl.item(r,c).setBackground(QColor.fromString("#eee"))
#					else:
#						tbl.item(r,c).setBackground(QBrush())
		return impl

	@Slot(QPoint)
	def tbl_context_menu(self, point):
		print(f"context menu for {point}")

	@Slot()
	@log_timer()
	def load_cmaps(self):
		populated = self.populated
		self.populated = [False]*(len(self.tables)+1)
		self.cmaps = {"None": None}
		selected = self.disp["cmap"]
		for cm in self.args.cmap:
			self.cmaps |= cmap.from_file(cm)
		sel = self.ui.sel_cmap
		sel.clear()
		sel.addItems(self.cmaps.keys())
		#print(f"current cmap {selected}")
		self.populated[self.tab] = populated[self.tab]
		self.populated[self.prefs_tab] = populated[self.prefs_tab]
		sel.setCurrentText(selected)
		if self.populated[self.tab]:
			self.update_cmap()

	@log_timer()
	def update_cmap(self):
		if self.disp["cmap"] == "None":
			#print("no cmap")
			self.ui.sel_cmap_inv.setEnabled(False)
			self.active_cmap = None
			self.cmap_widget.setText("None")
		else:
			#print(f"current cmap {self.disp['cmap']}")
			try:
				if self.disp["cmap_inv"]:
					#print("inverted")
					self.active_cmap = reversed(self.cmaps[self.disp["cmap"]])
				else:
					self.active_cmap = self.cmaps[self.disp["cmap"]]
				self.cmap_widget.setText(self.active_cmap.name)
			except KeyError:
				print(f"Resetting cmap because {self.disp['cmap']} doesn't exist")
				self.ui.sel_cmap.setCurrentText("None")
				# the docs say the signal is supposed to be emitted automatically
				# when setCurrentText is called, but it doesn't seem to be,
				# possibly to avoid infinite recursion. but "None" is guaranteed to
				# be handled above and not infinitely recurse
				self.set_disp_cmap("None")
				return False

		#print(self.disp)
		#print(self.active_cmap)
		self.update_vis_cmap()
		return True

	#@log_timer()
	def update_vis_cmap(self):
		label = self.ui.vis_cmap
		rect = label.size()
		borders = 2*label.frameWidth() + 2*label.margin()
		width = (rect.width() - borders)
		print(f"{time.strftime('%H:%M:%S')}: resize: {rect};{width}")
		if self.active_cmap is None:
			label.clear()
			return

		#if not self.cmap_img:
		self.cmap_img = QImage(width, 1, QImage.Format.Format_RGB32)
		self.cmap_img.fill(QColor.fromRgbF(0xee,0xfe,0xef))
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
		if not self.populated[self.prefs_tab]:
			return
		token_supply[C.CASH] = val
		self.update_curs()
	@Slot(int)
	def set_coal(self, val):
		if not self.populated[self.prefs_tab]:
			return
		token_supply[C.COAL] = val
		self.update_curs()
	@Slot(int)
	def set_diesel(self, val):
		if not self.populated[self.prefs_tab]:
			return
		token_supply[C.DIESEL] = val
		self.update_curs()
	@Slot(int)
	def set_electric(self, val):
		if not self.populated[self.prefs_tab]:
			return
		token_supply[C.ELECTRIC] = val
		self.update_curs()
	@Slot(int)
	def set_disp_unit(self, val):
		if not self.populated[self.prefs_tab]:
			return
		self.disp["unit"] = val
		self.update_units()
	@Slot(str)
	def set_disp_cmap(self, val):
		#print(f"set_disp_cmap(self, {repr(val)}")
		self.disp["cmap"] = val
		self.ui.sel_cmap_inv.setEnabled(val != "None")
		if self.populated[self.prefs_tab]:
			self.update_cmap()
	@Slot(int)
	def set_disp_cmap_inv(self, val):
		self.disp["cmap_inv"] = bool(val)
		if self.populated[self.prefs_tab]:
			self.update_cmap()


if __name__ == "__main__":
	app = QApplication(sys.argv)

	window = MainWindow(app, sys.argv)
	window.show()

	sys.exit(app.exec())

# Todo:
# I haven't quite decided if I'm going to do a custom model/view thing or use a
#	QSqlTableModel with an in-memory sqlite3 db
# Add search
# Add column hiding
# Probably replace my custom field with dataclasses.field and use its metadata
# Either hook up the file>Open actions with QDialog or remove them
