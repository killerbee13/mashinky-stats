# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel
#from PySide6.QtWidgets import

from row import Row

# QSQLITE_ENABLE_REGEXP
class TableModel(QAbstractTableModel):
	data: list[Row]
	def __init__(self):
		super().__init__()
		pass

class Proxy(QSortFilterProxyModel):
	pass
