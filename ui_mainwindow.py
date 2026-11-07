# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QGridLayout,
    QGroupBox, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QSizePolicy,
    QSpinBox, QStatusBar, QTabWidget, QTableWidget,
    QTableWidgetItem, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1183, 782)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        icon = QIcon()
        iconThemeName = u"system-file-manager"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionOpen.setIcon(icon)
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        icon1 = QIcon()
        iconThemeName = u"window-close"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionQuit.setIcon(icon1)
        self.actionMods = QAction(MainWindow)
        self.actionMods.setObjectName(u"actionMods")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setLayoutDirection(Qt.LeftToRight)
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tab_engines = QWidget()
        self.tab_engines.setObjectName(u"tab_engines")
        self.gridLayout = QGridLayout(self.tab_engines)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tbl_engines = QTableWidget(self.tab_engines)
        self.tbl_engines.setObjectName(u"tbl_engines")
        self.tbl_engines.horizontalHeader().setProperty(u"showSortIndicator", True)
        self.tbl_engines.verticalHeader().setProperty(u"showSortIndicator", False)

        self.gridLayout.addWidget(self.tbl_engines, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_engines, "")
        self.tab_wagons = QWidget()
        self.tab_wagons.setObjectName(u"tab_wagons")
        self.gridLayout_3 = QGridLayout(self.tab_wagons)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.tbl_wagons = QTableWidget(self.tab_wagons)
        if (self.tbl_wagons.columnCount() < 3):
            self.tbl_wagons.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tbl_wagons.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tbl_wagons.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tbl_wagons.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.tbl_wagons.setObjectName(u"tbl_wagons")
        self.tbl_wagons.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_3.addWidget(self.tbl_wagons, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_wagons, "")
        self.tab_vehicles = QWidget()
        self.tab_vehicles.setObjectName(u"tab_vehicles")
        self.gridLayout_4 = QGridLayout(self.tab_vehicles)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.tbl_vehicles = QTableWidget(self.tab_vehicles)
        self.tbl_vehicles.setObjectName(u"tbl_vehicles")
        self.tbl_vehicles.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_4.addWidget(self.tbl_vehicles, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_vehicles, "")
        self.tab_aircraft = QWidget()
        self.tab_aircraft.setObjectName(u"tab_aircraft")
        self.gridLayout_5 = QGridLayout(self.tab_aircraft)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.tbl_aircraft = QTableWidget(self.tab_aircraft)
        self.tbl_aircraft.setObjectName(u"tbl_aircraft")
        self.tbl_aircraft.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_5.addWidget(self.tbl_aircraft, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_aircraft, "")
        self.tab_all = QWidget()
        self.tab_all.setObjectName(u"tab_all")
        self.gridLayout_8 = QGridLayout(self.tab_all)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.tbl_all = QTableWidget(self.tab_all)
        self.tbl_all.setObjectName(u"tbl_all")
        self.tbl_all.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_8.addWidget(self.tbl_all, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_all, "")
        self.tab_prefs = QWidget()
        self.tab_prefs.setObjectName(u"tab_prefs")
        self.groupBox_tokens = QGroupBox(self.tab_prefs)
        self.groupBox_tokens.setObjectName(u"groupBox_tokens")
        self.groupBox_tokens.setGeometry(QRect(9, 9, 281, 93))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_tokens.sizePolicy().hasHeightForWidth())
        self.groupBox_tokens.setSizePolicy(sizePolicy1)
        self.gridLayout_6 = QGridLayout(self.groupBox_tokens)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.amt_electricity = QSpinBox(self.groupBox_tokens)
        self.amt_electricity.setObjectName(u"amt_electricity")
        self.amt_electricity.setMaximum(10000)
        self.amt_electricity.setSingleStep(10)
        self.amt_electricity.setValue(250)

        self.gridLayout_6.addWidget(self.amt_electricity, 2, 3, 1, 1)

        self.label_electricity = QLabel(self.groupBox_tokens)
        self.label_electricity.setObjectName(u"label_electricity")

        self.gridLayout_6.addWidget(self.label_electricity, 1, 3, 1, 1)

        self.label_coal = QLabel(self.groupBox_tokens)
        self.label_coal.setObjectName(u"label_coal")

        self.gridLayout_6.addWidget(self.label_coal, 1, 1, 1, 1)

        self.label_diesel = QLabel(self.groupBox_tokens)
        self.label_diesel.setObjectName(u"label_diesel")

        self.gridLayout_6.addWidget(self.label_diesel, 1, 2, 1, 1)

        self.amt_cash = QSpinBox(self.groupBox_tokens)
        self.amt_cash.setObjectName(u"amt_cash")
        self.amt_cash.setFrame(True)
        self.amt_cash.setMaximum(10000)
        self.amt_cash.setSingleStep(10)
        self.amt_cash.setValue(1000)

        self.gridLayout_6.addWidget(self.amt_cash, 2, 0, 1, 1, Qt.AlignTop)

        self.amt_coal = QSpinBox(self.groupBox_tokens)
        self.amt_coal.setObjectName(u"amt_coal")
        self.amt_coal.setMaximum(10000)
        self.amt_coal.setSingleStep(10)
        self.amt_coal.setValue(500)

        self.gridLayout_6.addWidget(self.amt_coal, 2, 1, 1, 1)

        self.amt_diesel = QSpinBox(self.groupBox_tokens)
        self.amt_diesel.setObjectName(u"amt_diesel")
        self.amt_diesel.setMaximum(10000)
        self.amt_diesel.setSingleStep(10)
        self.amt_diesel.setValue(250)

        self.gridLayout_6.addWidget(self.amt_diesel, 2, 2, 1, 1)

        self.label_cash = QLabel(self.groupBox_tokens)
        self.label_cash.setObjectName(u"label_cash")

        self.gridLayout_6.addWidget(self.label_cash, 1, 0, 1, 1)

        self.groupBox_display = QGroupBox(self.tab_prefs)
        self.groupBox_display.setObjectName(u"groupBox_display")
        self.groupBox_display.setGeometry(QRect(10, 110, 281, 151))
        sizePolicy1.setHeightForWidth(self.groupBox_display.sizePolicy().hasHeightForWidth())
        self.groupBox_display.setSizePolicy(sizePolicy1)
        self.groupBox_display.setMaximumSize(QSize(16777215, 151))
        self.groupBox_display.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.groupBox_display.setFlat(False)
        self.groupBox_display.setCheckable(False)
        self.formLayout = QFormLayout(self.groupBox_display)
        self.formLayout.setObjectName(u"formLayout")
        self.label_unit = QLabel(self.groupBox_display)
        self.label_unit.setObjectName(u"label_unit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_unit.sizePolicy().hasHeightForWidth())
        self.label_unit.setSizePolicy(sizePolicy2)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_unit)

        self.sel_unit = QComboBox(self.groupBox_display)
        self.sel_unit.addItem("")
        self.sel_unit.addItem("")
        self.sel_unit.setObjectName(u"sel_unit")
        sizePolicy2.setHeightForWidth(self.sel_unit.sizePolicy().hasHeightForWidth())
        self.sel_unit.setSizePolicy(sizePolicy2)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.sel_unit)

        self.label_cmap = QLabel(self.groupBox_display)
        self.label_cmap.setObjectName(u"label_cmap")
        sizePolicy2.setHeightForWidth(self.label_cmap.sizePolicy().hasHeightForWidth())
        self.label_cmap.setSizePolicy(sizePolicy2)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_cmap)

        self.sel_cmap = QComboBox(self.groupBox_display)
        self.sel_cmap.addItem("")
        self.sel_cmap.addItem("")
        self.sel_cmap.addItem("")
        self.sel_cmap.setObjectName(u"sel_cmap")
        sizePolicy2.setHeightForWidth(self.sel_cmap.sizePolicy().hasHeightForWidth())
        self.sel_cmap.setSizePolicy(sizePolicy2)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.sel_cmap)

        self.groupBox = QGroupBox(self.tab_prefs)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 270, 281, 151))
        self.gridLayout_7 = QGridLayout(self.groupBox)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_moddir = QLabel(self.groupBox)
        self.label_moddir.setObjectName(u"label_moddir")

        self.gridLayout_7.addWidget(self.label_moddir, 0, 0, 1, 1)

        self.lineEdit_others = QLineEdit(self.groupBox)
        self.lineEdit_others.setObjectName(u"lineEdit_others")

        self.gridLayout_7.addWidget(self.lineEdit_others, 3, 0, 1, 1)

        self.lineEdit_moddir = QLineEdit(self.groupBox)
        self.lineEdit_moddir.setObjectName(u"lineEdit_moddir")
        self.lineEdit_moddir.setReadOnly(False)

        self.gridLayout_7.addWidget(self.lineEdit_moddir, 1, 0, 1, 1)

        self.label_others = QLabel(self.groupBox)
        self.label_others.setObjectName(u"label_others")

        self.gridLayout_7.addWidget(self.label_others, 2, 0, 1, 1)

        self.tabWidget.addTab(self.tab_prefs, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1183, 22))
        self.menuFiles = QMenu(self.menubar)
        self.menuFiles.setObjectName(u"menuFiles")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFiles.menuAction())
        self.menuFiles.addAction(self.actionOpen)
        self.menuFiles.addAction(self.actionMods)
        self.menuFiles.addSeparator()
        self.menuFiles.addAction(self.actionQuit)

        self.retranslateUi(MainWindow)
        self.actionQuit.triggered.connect(MainWindow.close)
        self.actionOpen.triggered.connect(MainWindow.open)
        self.actionMods.triggered.connect(MainWindow.open)
        self.amt_cash.valueChanged.connect(MainWindow.set_cash)
        self.amt_coal.valueChanged.connect(MainWindow.set_coal)
        self.amt_diesel.valueChanged.connect(MainWindow.set_diesel)
        self.amt_electricity.valueChanged.connect(MainWindow.set_electricity)
        self.sel_unit.currentIndexChanged.connect(MainWindow.set_disp_unit)
        self.sel_cmap.currentIndexChanged.connect(MainWindow.set_disp_cmap)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mashinky Stats Viewer", None))
        MainWindow.setProperty(u"ModDir", "")
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open Files...", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
#if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionMods.setText(QCoreApplication.translate("MainWindow", u"Open Mods Folder...", None))
#if QT_CONFIG(shortcut)
        self.actionMods.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+M", None))
#endif // QT_CONFIG(shortcut)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_engines), QCoreApplication.translate("MainWindow", u"Engines", None))
        ___qtablewidgetitem = self.tbl_wagons.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Name", None))
        ___qtablewidgetitem1 = self.tbl_wagons.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"ID", None))
        ___qtablewidgetitem2 = self.tbl_wagons.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Source", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_wagons), QCoreApplication.translate("MainWindow", u"Wagons", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_vehicles), QCoreApplication.translate("MainWindow", u"Vehicles", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_aircraft), QCoreApplication.translate("MainWindow", u"Aircraft", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_all), QCoreApplication.translate("MainWindow", u"All", None))
        self.groupBox_tokens.setTitle(QCoreApplication.translate("MainWindow", u"Tokens Budgets", None))
        self.label_electricity.setText(QCoreApplication.translate("MainWindow", u"Electricity", None))
        self.label_coal.setText(QCoreApplication.translate("MainWindow", u"Coal", None))
        self.label_diesel.setText(QCoreApplication.translate("MainWindow", u"Diesel", None))
        self.label_cash.setText(QCoreApplication.translate("MainWindow", u"Cash", None))
        self.groupBox_display.setTitle(QCoreApplication.translate("MainWindow", u"Display", None))
        self.label_unit.setText(QCoreApplication.translate("MainWindow", u"Speed unit", None))
        self.sel_unit.setItemText(0, QCoreApplication.translate("MainWindow", u"kmph", None))
        self.sel_unit.setItemText(1, QCoreApplication.translate("MainWindow", u"mph", None))

        self.label_cmap.setText(QCoreApplication.translate("MainWindow", u"Colormap", None))
        self.sel_cmap.setItemText(0, QCoreApplication.translate("MainWindow", u"None", None))
        self.sel_cmap.setItemText(1, QCoreApplication.translate("MainWindow", u"Yellow-Blue", None))
        self.sel_cmap.setItemText(2, QCoreApplication.translate("MainWindow", u"Red-Green", None))

        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Files", None))
        self.label_moddir.setText(QCoreApplication.translate("MainWindow", u"Mods folder", None))
        self.label_others.setText(QCoreApplication.translate("MainWindow", u"Other files", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_prefs), QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.menuFiles.setTitle(QCoreApplication.translate("MainWindow", u"Files", None))
    # retranslateUi

