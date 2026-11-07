# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget,
	QTableWidgetItem)
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QColor
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
	def __init__(self, argv):
		super(MainWindow, self).__init__()

		args, self.files = handle_cli(True)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.disp = {"unit": 0, "cmap": 0}

		self.ui.amt_cash.setValue(token_supply[C.CASH])
		self.ui.amt_coal.setValue(token_supply[C.COAL])
		self.ui.amt_diesel.setValue(token_supply[C.DIESEL])
		self.ui.amt_electricity.setValue(token_supply[C.ELECTRIC])

		self.engine_labels = labels_by_type['engine']
		self.wagon_labels = labels_by_type['wagon']
		self.vehicle_labels = labels_by_type['vehicle']
		self.aircraft_labels = labels_by_type['aircraft']
		self.all_labels = labels_by_type['all']

		self.data = read_files(self.files)
		self.engines = [row for row in self.data if filter_engine(row)]
		self.wagons = [row for row in self.data if filter_wagon(row)]
		self.vehicles = [row for row in self.data if filter_vehicle(row)]
		self.aircraft = [row for row in self.data if filter_aircraft(row)]

		self.tables = [
			(self.ui.tbl_engines, self.engine_labels, self.engines),
			(self.ui.tbl_wagons, self.wagon_labels, self.wagons),
			(self.ui.tbl_vehicles, self.vehicle_labels, self.vehicles),
			(self.ui.tbl_aircraft, self.aircraft_labels, self.aircraft),
			(self.ui.tbl_all, self.all_labels, []),
			#(self.ui.tbl_all, self.all_labels, self.data),
		]
		self.headers = [
			(tbl, tbl.horizontalHeader(), tbl.verticalHeader())
			for tbl, _, _ in self.tables
		]


		for tbl, labels, data in self.tables:
			self.populate_table(tbl, labels, data)

		for tbl, hh, vh in self.headers:
			tbl.setSortingEnabled(True)
			hh.setSectionsMovable(True)
			tbl.cellClicked.connect(self.tbl_click(tbl))

		sizes = [(tbl.columnCount(), tbl.rowCount()) for tbl, l, d in self.tables]

		self.statusBar().showMessage(
			", ".join([f"{h}*{w}={w*h}" for (w, h) in sizes])
			+ " cells, " + str(sum((w*h for w, h in sizes))) + " total")


	def populate_table(self, table, labels, data):
		table.setColumnCount(len(labels))
		table.setHorizontalHeaderLabels(labels)
		table.setRowCount(len(data))
		table.setVerticalHeaderLabels([row[C.NAME] for row in data])
		for r, v in enumerate(data):
			for c, f in enumerate(labels):
				item = QTableWidgetItem(str(rnd(v[f])))
				table.setItem(r, c, item)
				pls_help_bug.append(None)
		h = table.horizontalHeader()
		#h.sectionClicked.connect(self.reset_labels(table))
		h.sortIndicatorChanged.connect(self.reset_labels(table))
		h.setSortIndicatorClearable(True)
		h.hideSection(0)
		table.sortItems(0, Qt.SortOrder.AscendingOrder)

	def update_views(self):
		counts = []
		for tbl, labels, data in self.tables:
			sort = tbl.isSortingEnabled()
			tbl.setSortingEnabled(False)
			count = 0
			for r in range(len(data)):
				old = data[r].copy()
				data[r] = all_stats(data[r], data[r][C.SOURCE])
				row = data[r]
				if tbl.rowCount() > 0:
					for c, f in enumerate(labels):
						if row[f] != old[f]:
							tbl.item(r,c).setText(str(rnd(row[f])))
							tbl.item(r,c).setBackground(QColor.fromRgb(255, 224, 224))
							count = count + 1
						else:
							tbl.item(r,c).setBackground(QColor.fromRgb(255, 255, 255))
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
			print(f"reset({v}, {o})")
			if v == -1:
				tbl.sortItems(0, Qt.SortOrder.AscendingOrder)
			tbl.sortItems(tbl.horizontalHeader().sortIndicatorSection(), o)
			self.reset_labels_for(tbl)
		return impl

	def reset_labels_for(self, tbl):
		for r in range(tbl.rowCount()):
			#print(r)
			#print(f"set v{r} from {tbl.verticalHeaderItem(r).text()} to {tbl.item(r,0).text()}")
			tbl.verticalHeaderItem(r).setText(tbl.item(r,0).text())

	def tbl_click(self, tbl):
		@Slot(int, int)
		def impl(cr, cc):
			print(f"tbl_click({cr},{cc})")
			for r in range(tbl.rowCount()):
				for c in range(tbl.columnCount()):
					pls_help_bug.append(None)
					if r == cr:
						tbl.item(r, c).setBackground(QColor.fromString("#eee"))
					else:
						tbl.item(r, c).setBackground(QColor.fromString("#fff"))
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
		token_supply[C.CASH] = val
		print(token_supply)
		self.update_views()
	@Slot(int)
	def set_coal(self, val):
		token_supply[C.COAL] = val
		print(token_supply)
		self.update_views()
	@Slot(int)
	def set_diesel(self, val):
		token_supply[C.DIESEL] = val
		print(token_supply)
		self.update_views()
	@Slot(int)
	def set_electricity(self, val):
		token_supply[C.ELECTRIC] = val
		print(token_supply)
		self.update_views()
	@Slot(int)
	def set_disp_unit(self, val):
		self.disp["unit"] = val
		print(self.disp)
		self.update_views()
	@Slot(int)
	def set_disp_cmap(self, val):
		self.disp["cmap"] = val
		print(self.disp)
		self.update_views()


if __name__ == "__main__":
	app = QApplication(sys.argv)

	window = MainWindow(sys.argv)
	window.show()

	sys.exit(app.exec())
