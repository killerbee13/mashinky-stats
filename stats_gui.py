# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget,
	QTableWidgetItem)
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QColor, QBrush, QFontMetrics
from ui_mainwindow import Ui_MainWindow
from mashinky_stats import (handle_cli, read_files, all_stats,
	filter_engine, filter_wagon, filter_vehicle, filter_aircraft,
	token_supply, labels_by_type, rnd)
import constants as C

pls_help_bug = []

def rgb_from_hex(code):
	code_hex = code.replace("#", "")
	rgb = tuple(int(code_hex[i:i+2], 16) for i in (0, 2, 4))
	return QColor.fromRgb(rgb[0], rgb[1], rgb[2])

class MainWindow(QMainWindow):
	engine_labels = labels_by_type['engine'].copy()
	wagon_labels = labels_by_type['wagon'].copy()
	vehicle_labels = labels_by_type['vehicle'].copy()
	aircraft_labels = labels_by_type['aircraft'].copy()
	all_labels = labels_by_type['all'].copy()
	disp = {"unit": 0, "cmap": 0}
	data = []
	tables = []
	ui = Ui_MainWindow()
	populated = False

	def __init__(self, argv):
		super(MainWindow, self).__init__()

		self.args, self.files, self.vfiles = handle_cli(True)
		self.ui.setupUi(self)

		self.ui.amt_cash.setValue(token_supply[C.CASH])
		self.ui.amt_coal.setValue(token_supply[C.COAL])
		self.ui.amt_diesel.setValue(token_supply[C.DIESEL])
		self.ui.amt_electricity.setValue(token_supply[C.ELECTRIC])

		self.ui.lineEdit_others.setText(" ".join(self.args.files))
		self.ui.lineEdit_moddir.setText(" ".join(self.args.path))
		self.ui.lineEdit_vfiles.setText(" ".join(self.args.vanilla))
		self.ui.lineEdit_vdir.setText(" ".join(self.args.vanilla_dir))

		self.update_data()

		self.tables = [
			(self.ui.tbl_engines, self.engine_labels, self.engines),
			(self.ui.tbl_wagons, self.wagon_labels, self.wagons),
			(self.ui.tbl_vehicles, self.vehicle_labels, self.vehicles),
			(self.ui.tbl_aircraft, self.aircraft_labels, self.aircraft),
			(self.ui.tbl_all, self.all_labels, self.data[:250]),
			#(self.ui.tbl_all, self.all_labels, self.data),
		]

		for tbl, labels, data in self.tables:
			labels.append(C.VANILLA)
			labels.append('index')
			self.populate_table(tbl, labels, data)
			h = tbl.horizontalHeader()
			h.setSectionsMovable(True)
			h.setSortIndicatorClearable(True)
			tbl.setSortingEnabled(True)
			tbl.cellClicked.connect(self.tbl_click(tbl))
			self.reset_labels_for(tbl)
		self.populated = True

		sizes = [(tbl.columnCount(), tbl.rowCount()) for tbl, l, d in self.tables]

		self.statusBar().showMessage(
			", ".join([f"{h}*{w}={w*h}" for (w, h) in sizes])
			+ " cells, " + str(sum((w*h for w, h in sizes))) + " total")

	def update_data(self):
		self.data = read_files(self.files, self.vfiles)

		self.engines = list(filter(filter_engine, self.data))
		self.wagons = list(filter(filter_wagon, self.data))
		self.vehicles = list(filter(filter_vehicle, self.data))
		self.aircraft = list(filter(filter_aircraft, self.data))

	def populate_table(self, table, labels, data):
		table.setColumnCount(len(labels))
		table.setHorizontalHeaderLabels(labels)
		table.setRowCount(len(data))
		table.setVerticalHeaderLabels([row[C.NAME] for row in data])
		for r, v in enumerate(data):
			for c, f in enumerate(labels):
				if f == 'index':
					item = QTableWidgetItem(('     '+str(v[f]))[-5:])
				else:
					item = QTableWidgetItem(str(rnd(v[f])))
				if QFontMetrics(item.font()).horizontalAdvance(item.text()) > table.columnWidth(c):
					item.setToolTip(str(rnd(v[f])))
				table.setItem(r, c, item)
				pls_help_bug.append(None)
		h = table.horizontalHeader()
		#h.sectionClicked.connect(self.reset_labels(table))
		h.sortIndicatorChanged.connect(self.reset_labels(table))
		h.hideSection(0)
		table.sortItems(0, Qt.SortOrder.AscendingOrder)

	@Slot()
	def update_views(self):
		if not self.populated:
			return
		counts = []
		for r in range(len(self.data)):
			self.data[r] = all_stats(self.data[r])
		for tbl, labels, data in self.tables:
			sort = tbl.isSortingEnabled()
			tbl.setSortingEnabled(False)
			count = 0
			for r in range(tbl.rowCount()):
				old = data[r].copy()
				data[r] = all_stats(data[r])
				row = data[r]
				for c, f in enumerate(labels):
					if row[f] != old[f]:
						tbl.item(r,c).setText(str(rnd(row[f])))
						tbl.item(r,c).setBackground(QColor.fromRgb(255, 224, 224))
						count = count + 1
					else:
						tbl.item(r,c).setBackground(QBrush())
					pls_help_bug.append(None)
			counts.append(count)
			if (sort):
				tbl.setSortingEnabled(True)
				self.reset_labels_for(tbl)
		self.statusBar().showMessage("Updated " + ", ".join(
			(str(c) for c in counts)) + " items")

	def reset_labels(self, tbl):
		@Slot(int, Qt.SortOrder)
		def impl(v, o):
			if self.populated:
				print(f"reset({v}, {o})")
			if v == -1:
				tbl.sortItems(0, Qt.SortOrder.AscendingOrder)
			tbl.sortItems(tbl.horizontalHeader().sortIndicatorSection(), o)
			self.reset_labels_for(tbl)
		return impl

	def reset_labels_for(self, tbl):
		van_idx = -1
		name_idx = -1
		for c in range(tbl.columnCount()):
			if tbl.horizontalHeaderItem(c).text() == C.VANILLA:
				van_idx = c
			if tbl.horizontalHeaderItem(c).text() == C.NAME:
				name_idx = c
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

#		colors = [("Red", "#FF0000"),
#		          ("Green", "#00FF00"),
#		          ("Blue", "#0000FF"),
#		          ("Black", "#000000"),
#		          ("White", "#FFFFFF"),
#		          ("Electric Green", "#41CD52"),
#		          ("Dark Blue", "#222840"),
#		          ("Yellow", "#F9E56d")]
#		self.ui.tbl_engines.setRowCount(len(colors))
#		self.ui.tbl_engines.setColumnCount(len(colors[0]) + 1)
#		self.ui.tbl_engines.setHorizontalHeaderLabels(["Name", "Hex Code", "Color"])
#		for i, (name, code) in enumerate(colors):
#			item_name = QTableWidgetItem(name)
#			item_code = QTableWidgetItem(code)
#			item_color = QTableWidgetItem()
#			item_color.setBackground(get_rgb_from_hex(code))
#			self.ui.tbl_engines.setItem(i, 0, item_name)
#			self.ui.tbl_engines.setItem(i, 1, item_code)
#			self.ui.tbl_engines.setItem(i, 2, item_color)

	@Slot()
	def open(self):
		print("open")

	@Slot(int)
	def set_cash(self, val):
		if not self.populated:
			return
		token_supply[C.CASH] = val
		print(token_supply)
		self.update_views()
	@Slot(int)
	def set_coal(self, val):
		if not self.populated:
			return
		token_supply[C.COAL] = val
		print(token_supply)
		self.update_views()
	@Slot(int)
	def set_diesel(self, val):
		if not self.populated:
			return
		token_supply[C.DIESEL] = val
		print(token_supply)
		self.update_views()
	@Slot(int)
	def set_electricity(self, val):
		if not self.populated:
			return
		token_supply[C.ELECTRIC] = val
		print(token_supply)
		self.update_views()
	@Slot(int)
	def set_disp_unit(self, val):
		if not self.populated:
			return
		self.disp["unit"] = val
		print(self.disp)
		self.update_views()
	@Slot(int)
	def set_disp_cmap(self, val):
		if not self.populated:
			return
		self.disp["cmap"] = val
		print(self.disp)
		self.update_views()

class Table:
	pass
# QSQLITE_ENABLE_REGEXP


if __name__ == "__main__":
	app = QApplication(sys.argv)

	window = MainWindow(sys.argv)
	window.show()

	sys.exit(app.exec())

# Todo:
# Go over the available columns and their order; hook up the speed units setting
# Add cmaps and highlighting
# I haven't quite decided if I'm going to do a custom model/view thing or use a QSqlTableModel with an in-memory sqlite3 db
# Add search
# Add column hiding
