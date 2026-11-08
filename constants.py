# This Python file uses the following encoding: utf-8
import collections
from dataclasses import dataclass

# Physical/mathematical constants
KM_PER_MI = 1.609344
TRACTION_SCALE = 42.1

# Column labels
# technical
ID = "id"
CID = "cargo id"
SOURCE = "source"
VANILLA = "vanilla"
# common
NAME = "Name"
LENGTH = "Length (u)"
WEIGHT = "Weight (t)"
EPOCHS = "Epochs"
ERA = "Era"
ERAS = "Eras"
TRACK = "Track"
# train-specific
CD6 = "CD(6) (t/6u)"
CD8 = "CD(8) (t/8u)"
# wagon-specific
COMPOUND_EFFICIENCY = "Compound Efficiency"
COMPOUND_PROFITABILITY = "Compound Profitability"
DENSITY = "Density"
WT_PER_CARGO = "Wt/Cargo"
CARGO_UNIT_WT = "Cargo Unit Wt"
# prime movers
SPEED = "Speed (km/hr)"
SPEED_MPH = "Speed (mph)"
POWER = "Power (hp)"
TRACTION = "Traction (t)"
TOWAGE = "Towage (t)"
THROUGHPUT = "Throughput (t*km/hr)"
PWT_FULL = "P/Wt loaded (hp/t)"
PWT_EMPTY = "P/Wt unloaded (hp/t)"
TOW_PER_LENGTH = "Tow/length (t/u)"
POWER_PER_LENGTH = "Power/length (hp/u)"
# cargo carriers
TYPE = "Type"
CARGO = "Cargo"
WEIGHT_FULL = "Wt. Loaded (t)"
WEIGHT_EMPTY = "Wt. Unloaded (t)"
BONUS = "Bonus"
PROFITABILITY = "Profitability (Cargo*Bonus)"
CARGO_PER_LENGTH = "Cargo/Length"
PROFIT_PER_LENGTH = "Profit/Length"
CARGO_PER_WT = "10 Cargo/Wt."
PROFIT_PER_WT = "10 Profit/Wt."
# single/multiple units (i.e. power and capacity both != 0)
TP_CARGO = "Cargo Throughput"
TP_PROFIT = "Profit Throughput"
# fuel
ADJCOST = "Adjusted Cost (share of all tokens produced)"
# throughput ratios
TP_ADJCOST = "TP/AdjCost"
TP_CASH = "TP/Cash"
TP_COAL = "TP/Coal"
TP_DIESEL = "TP/Diesel"
TP_ELECTRIC = "TP/Electric"
TPC_ADJCOST = "TPc/AdjCost"
TPP_ADJCOST = "TPp/AdjCost"
TPC_CASH = "TPc/Cash"
TPP_CASH = "TPp/Cash"
TPC_COAL = "TPc/Coal"
TPP_COAL = "TPp/Coal"
TPC_DIESEL = "TPc/Diesel"
TPP_DIESEL = "TPp/Diesel"
TPC_ELECTRIC = "TPc/Electric"
TPP_ELECTRIC = "TPp/Electric"
COSTS_RAW = "Costs (raw)"

#Tokens
CASH = "Cash"
COAL = "Coal"
DIESEL = "Diesel"
ELECTRIC = "Electric"

# Cargo types
# coal, diesel already covered
PASSENGER = "Passenger"
MAIL = "Mail"
LOGS = "Logs"
LUMBER = "Lumber"
PASS_ENGINE = "Pass. Engine"
MAIL_ENGINE = "Mail Engine"
# coal
ORE = "Ore"
IRON = "Iron"
OIL = "Oil"
# diesel
GOODS = "Goods"
SAND = "Sand"
STEEL = "Steel"
FOOD = "Food"
LIMESTONE = "Limestone"
CEMENT = "Cement"
GARBAGE = "Garbage"

