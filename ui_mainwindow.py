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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QFormLayout,
    QFrame, QGridLayout, QGroupBox, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QSpacerItem, QSpinBox,
    QStatusBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

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
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.frame_search = QFrame(self.centralwidget)
        self.frame_search.setObjectName(u"frame_search")
        self.frame_search.setFrameShape(QFrame.NoFrame)
        self.frame_search.setFrameShadow(QFrame.Plain)
        self.gridLayout_9 = QGridLayout(self.frame_search)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.lineEdit_search = QLineEdit(self.frame_search)
        self.lineEdit_search.setObjectName(u"lineEdit_search")

        self.gridLayout_9.addWidget(self.lineEdit_search, 1, 1, 1, 1)

        self.lbl_search = QLabel(self.frame_search)
        self.lbl_search.setObjectName(u"lbl_search")

        self.gridLayout_9.addWidget(self.lbl_search, 1, 0, 1, 1)


        self.gridLayout_2.addWidget(self.frame_search, 1, 0, 1, 1)

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
        self.tbl_engines.setAlternatingRowColors(True)
        self.tbl_engines.setCornerButtonEnabled(False)
        self.tbl_engines.horizontalHeader().setMinimumSectionSize(16)
        self.tbl_engines.horizontalHeader().setProperty(u"showSortIndicator", True)
        self.tbl_engines.verticalHeader().setProperty(u"showSortIndicator", False)

        self.gridLayout.addWidget(self.tbl_engines, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_engines, "")
        self.tab_wagons = QWidget()
        self.tab_wagons.setObjectName(u"tab_wagons")
        self.gridLayout_3 = QGridLayout(self.tab_wagons)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.tbl_wagons = QTableWidget(self.tab_wagons)
        self.tbl_wagons.setObjectName(u"tbl_wagons")
        self.tbl_wagons.setAlternatingRowColors(True)
        self.tbl_wagons.setCornerButtonEnabled(False)
        self.tbl_wagons.horizontalHeader().setMinimumSectionSize(16)
        self.tbl_wagons.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_3.addWidget(self.tbl_wagons, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_wagons, "")
        self.tab_vehicles = QWidget()
        self.tab_vehicles.setObjectName(u"tab_vehicles")
        self.gridLayout_4 = QGridLayout(self.tab_vehicles)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.tbl_vehicles = QTableWidget(self.tab_vehicles)
        self.tbl_vehicles.setObjectName(u"tbl_vehicles")
        self.tbl_vehicles.setAlternatingRowColors(True)
        self.tbl_vehicles.setCornerButtonEnabled(False)
        self.tbl_vehicles.horizontalHeader().setMinimumSectionSize(16)
        self.tbl_vehicles.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_4.addWidget(self.tbl_vehicles, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_vehicles, "")
        self.tab_aircraft = QWidget()
        self.tab_aircraft.setObjectName(u"tab_aircraft")
        self.gridLayout_5 = QGridLayout(self.tab_aircraft)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.tbl_aircraft = QTableWidget(self.tab_aircraft)
        self.tbl_aircraft.setObjectName(u"tbl_aircraft")
        self.tbl_aircraft.setAlternatingRowColors(True)
        self.tbl_aircraft.setCornerButtonEnabled(False)
        self.tbl_aircraft.horizontalHeader().setMinimumSectionSize(16)
        self.tbl_aircraft.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_5.addWidget(self.tbl_aircraft, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_aircraft, "")
        self.tab_all = QWidget()
        self.tab_all.setObjectName(u"tab_all")
        self.gridLayout_8 = QGridLayout(self.tab_all)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.tbl_all = QTableWidget(self.tab_all)
        self.tbl_all.setObjectName(u"tbl_all")
        self.tbl_all.setAlternatingRowColors(True)
        self.tbl_all.setCornerButtonEnabled(False)
        self.tbl_all.horizontalHeader().setMinimumSectionSize(16)
        self.tbl_all.horizontalHeader().setProperty(u"showSortIndicator", True)

        self.gridLayout_8.addWidget(self.tbl_all, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_all, "")
        self.tab_prefs = QWidget()
        self.tab_prefs.setObjectName(u"tab_prefs")
        self.verticalLayout = QVBoxLayout(self.tab_prefs)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_tokens = QGroupBox(self.tab_prefs)
        self.groupBox_tokens.setObjectName(u"groupBox_tokens")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_tokens.sizePolicy().hasHeightForWidth())
        self.groupBox_tokens.setSizePolicy(sizePolicy1)
        self.groupBox_tokens.setMaximumSize(QSize(16777215, 16777215))
        self.groupBox_tokens.setFlat(True)
        self.groupBox_tokens.setCheckable(False)
        self.gridLayout_6 = QGridLayout(self.groupBox_tokens)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.lbl_coal = QLabel(self.groupBox_tokens)
        self.lbl_coal.setObjectName(u"lbl_coal")

        self.gridLayout_6.addWidget(self.lbl_coal, 1, 1, 1, 1)

        self.amt_electric = QSpinBox(self.groupBox_tokens)
        self.amt_electric.setObjectName(u"amt_electric")
        self.amt_electric.setMaximum(10000)
        self.amt_electric.setSingleStep(10)
        self.amt_electric.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.amt_electric.setValue(250)

        self.gridLayout_6.addWidget(self.amt_electric, 2, 3, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer, 2, 4, 1, 1)

        self.lbl_cash = QLabel(self.groupBox_tokens)
        self.lbl_cash.setObjectName(u"lbl_cash")

        self.gridLayout_6.addWidget(self.lbl_cash, 1, 0, 1, 1)

        self.amt_coal = QSpinBox(self.groupBox_tokens)
        self.amt_coal.setObjectName(u"amt_coal")
        self.amt_coal.setMaximum(10000)
        self.amt_coal.setSingleStep(10)
        self.amt_coal.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.amt_coal.setValue(500)

        self.gridLayout_6.addWidget(self.amt_coal, 2, 1, 1, 1)

        self.lbl_electric = QLabel(self.groupBox_tokens)
        self.lbl_electric.setObjectName(u"lbl_electric")

        self.gridLayout_6.addWidget(self.lbl_electric, 1, 3, 1, 1)

        self.amt_diesel = QSpinBox(self.groupBox_tokens)
        self.amt_diesel.setObjectName(u"amt_diesel")
        self.amt_diesel.setMaximum(10000)
        self.amt_diesel.setSingleStep(10)
        self.amt_diesel.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.amt_diesel.setValue(250)

        self.gridLayout_6.addWidget(self.amt_diesel, 2, 2, 1, 1)

        self.lbl_diesel = QLabel(self.groupBox_tokens)
        self.lbl_diesel.setObjectName(u"lbl_diesel")

        self.gridLayout_6.addWidget(self.lbl_diesel, 1, 2, 1, 1)

        self.amt_cash = QSpinBox(self.groupBox_tokens)
        self.amt_cash.setObjectName(u"amt_cash")
        self.amt_cash.setFrame(True)
        self.amt_cash.setMaximum(10000)
        self.amt_cash.setSingleStep(10)
        self.amt_cash.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.amt_cash.setValue(1000)

        self.gridLayout_6.addWidget(self.amt_cash, 2, 0, 1, 1, Qt.AlignTop)

        self.lbl_adj_cash = QLabel(self.groupBox_tokens)
        self.lbl_adj_cash.setObjectName(u"lbl_adj_cash")

        self.gridLayout_6.addWidget(self.lbl_adj_cash, 3, 0, 1, 1)

        self.lbl_adj_coal = QLabel(self.groupBox_tokens)
        self.lbl_adj_coal.setObjectName(u"lbl_adj_coal")

        self.gridLayout_6.addWidget(self.lbl_adj_coal, 3, 1, 1, 1)

        self.lbl_adj_diesel = QLabel(self.groupBox_tokens)
        self.lbl_adj_diesel.setObjectName(u"lbl_adj_diesel")

        self.gridLayout_6.addWidget(self.lbl_adj_diesel, 3, 2, 1, 1)

        self.lbl_adj_electric = QLabel(self.groupBox_tokens)
        self.lbl_adj_electric.setObjectName(u"lbl_adj_electric")

        self.gridLayout_6.addWidget(self.lbl_adj_electric, 3, 3, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_tokens)

        self.groupBox_display = QGroupBox(self.tab_prefs)
        self.groupBox_display.setObjectName(u"groupBox_display")
        sizePolicy1.setHeightForWidth(self.groupBox_display.sizePolicy().hasHeightForWidth())
        self.groupBox_display.setSizePolicy(sizePolicy1)
        self.groupBox_display.setMaximumSize(QSize(16777215, 151))
        self.groupBox_display.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.groupBox_display.setFlat(True)
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


        self.verticalLayout.addWidget(self.groupBox_display)

        self.groupBox = QGroupBox(self.tab_prefs)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setFlat(True)
        self.gridLayout_7 = QGridLayout(self.groupBox)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.lineEdit_vdir = QLineEdit(self.groupBox)
        self.lineEdit_vdir.setObjectName(u"lineEdit_vdir")
        self.lineEdit_vdir.setReadOnly(True)

        self.gridLayout_7.addWidget(self.lineEdit_vdir, 5, 0, 1, 1)

        self.lineEdit_moddir = QLineEdit(self.groupBox)
        self.lineEdit_moddir.setObjectName(u"lineEdit_moddir")
        self.lineEdit_moddir.setReadOnly(True)

        self.gridLayout_7.addWidget(self.lineEdit_moddir, 1, 0, 1, 1)

        self.lbl_vdir = QLabel(self.groupBox)
        self.lbl_vdir.setObjectName(u"lbl_vdir")

        self.gridLayout_7.addWidget(self.lbl_vdir, 4, 0, 1, 1)

        self.lineEdit_others = QLineEdit(self.groupBox)
        self.lineEdit_others.setObjectName(u"lineEdit_others")
        self.lineEdit_others.setReadOnly(True)

        self.gridLayout_7.addWidget(self.lineEdit_others, 3, 0, 1, 1)

        self.lbl_others = QLabel(self.groupBox)
        self.lbl_others.setObjectName(u"lbl_others")

        self.gridLayout_7.addWidget(self.lbl_others, 2, 0, 1, 1)

        self.lbl_moddir = QLabel(self.groupBox)
        self.lbl_moddir.setObjectName(u"lbl_moddir")

        self.gridLayout_7.addWidget(self.lbl_moddir, 0, 0, 1, 1)

        self.lbl_vfiles = QLabel(self.groupBox)
        self.lbl_vfiles.setObjectName(u"lbl_vfiles")

        self.gridLayout_7.addWidget(self.lbl_vfiles, 6, 0, 1, 1)

        self.lineEdit_vfiles = QLineEdit(self.groupBox)
        self.lineEdit_vfiles.setObjectName(u"lineEdit_vfiles")
        self.lineEdit_vfiles.setReadOnly(True)

        self.gridLayout_7.addWidget(self.lineEdit_vfiles, 7, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tab_prefs, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.vis_cmap = QLabel(self.centralwidget)
        self.vis_cmap.setObjectName(u"vis_cmap")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(100)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.vis_cmap.sizePolicy().hasHeightForWidth())
        self.vis_cmap.setSizePolicy(sizePolicy3)
        self.vis_cmap.setMinimumSize(QSize(0, 24))
        self.vis_cmap.setFrameShape(QFrame.Panel)
        self.vis_cmap.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.vis_cmap, 4, 0, 1, 1)

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
        self.amt_coal.valueChanged.connect(MainWindow.set_coal)
        self.sel_unit.currentIndexChanged.connect(MainWindow.set_disp_unit)
        self.amt_cash.valueChanged.connect(MainWindow.set_cash)
        self.amt_diesel.valueChanged.connect(MainWindow.set_diesel)
        self.sel_cmap.currentIndexChanged.connect(MainWindow.set_disp_cmap)
        self.amt_electric.valueChanged.connect(MainWindow.set_electric)
        self.tabWidget.currentChanged.connect(MainWindow.update_table)

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
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.lbl_search.setText(QCoreApplication.translate("MainWindow", u"Search", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_engines), QCoreApplication.translate("MainWindow", u"Engines", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_wagons), QCoreApplication.translate("MainWindow", u"Wagons", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_vehicles), QCoreApplication.translate("MainWindow", u"Vehicles", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_aircraft), QCoreApplication.translate("MainWindow", u"Aircraft", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_all), QCoreApplication.translate("MainWindow", u"All", None))
        self.groupBox_tokens.setTitle(QCoreApplication.translate("MainWindow", u"Tokens Budgets", None))
        self.lbl_coal.setText(QCoreApplication.translate("MainWindow", u"Coal", None))
        self.lbl_cash.setText(QCoreApplication.translate("MainWindow", u"Cash", None))
        self.lbl_electric.setText(QCoreApplication.translate("MainWindow", u"Electricity", None))
        self.lbl_diesel.setText(QCoreApplication.translate("MainWindow", u"Diesel", None))
        self.lbl_adj_cash.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lbl_adj_coal.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lbl_adj_diesel.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.lbl_adj_electric.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.groupBox_display.setTitle(QCoreApplication.translate("MainWindow", u"Display", None))
        self.label_unit.setText(QCoreApplication.translate("MainWindow", u"Speed unit", None))
        self.sel_unit.setItemText(0, QCoreApplication.translate("MainWindow", u"kmph", None))
        self.sel_unit.setItemText(1, QCoreApplication.translate("MainWindow", u"mph", None))

        self.label_cmap.setText(QCoreApplication.translate("MainWindow", u"Colormap", None))
        self.sel_cmap.setItemText(0, QCoreApplication.translate("MainWindow", u"None", None))
        self.sel_cmap.setItemText(1, QCoreApplication.translate("MainWindow", u"Yellow-Blue", None))
        self.sel_cmap.setItemText(2, QCoreApplication.translate("MainWindow", u"Red-Green", None))

        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Files", None))
        self.lbl_vdir.setText(QCoreApplication.translate("MainWindow", u"Vanilla directories", None))
        self.lbl_others.setText(QCoreApplication.translate("MainWindow", u"Mod files", None))
        self.lbl_moddir.setText(QCoreApplication.translate("MainWindow", u"Mods folder", None))
        self.lbl_vfiles.setText(QCoreApplication.translate("MainWindow", u"Vanilla files", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_prefs), QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.vis_cmap.setText("")
        self.menuFiles.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

