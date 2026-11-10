from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
import constants as C

class Highlight(Enum):
	NONE = auto()
	HIGH = auto()
	LOW = auto()
	PARITY = auto()

@dataclass(kw_only=True, frozen=True)
class ColProps:
	type: type
	highlight: Highlight = Highlight.NONE
	generated: bool = True
	xml_key: Optional[str] = None

props = {
	'index': ColProps(type=int),
	C.ID: ColProps(type=str, generated=False),
	'vehicle_type': ColProps(type=str, generated=False),
	'name': ColProps(type=str, generated=False),
	'weight_full': ColProps(type=float, generated=False),
	'weight_empty': ColProps(type=float, generated=False),
	'epoch': ColProps(type=str, generated=False),
	'length': ColProps(type=float),
	'track': ColProps(type=int),
	C.CID: ColProps(type=str, generated=False),
	C.SOURCE: ColProps(type=str, generated=False),
	C.VANILLA: ColProps(type=bool, generated=False),
	C.NAME: ColProps(type=str),
	C.LENGTH: ColProps(type=float, highlight=Highlight.LOW, generated=False),
	C.WEIGHT: ColProps(type=float, highlight=Highlight.LOW),
	C.WEIGHT_FULL: ColProps(type=float, highlight=Highlight.LOW, generated=False),
	C.WEIGHT_EMPTY: ColProps(type=float, highlight=Highlight.LOW, generated=False),
	C.EPOCHS: ColProps(type=str),
	C.ERA: ColProps(type=int),
	C.ERAS: ColProps(type=str),
	C.TRACK: ColProps(type=int, generated=False),
	C.SPEED: ColProps(type=float, highlight=Highlight.HIGH, generated=False),
	C.SPEED_MPH: ColProps(type=int, highlight=Highlight.HIGH),
	C.POWER: ColProps(type=float, highlight=Highlight.HIGH, generated=False),
	C.TRACTION: ColProps(type=int, highlight=Highlight.HIGH),
	C.TOWAGE: ColProps(type=float, highlight=Highlight.HIGH),
	C.THROUGHPUT: ColProps(type=float, highlight=Highlight.HIGH),
	C.PWT_FULL: ColProps(type=float, highlight=Highlight.HIGH),
	C.PWT_EMPTY: ColProps(type=float, highlight=Highlight.HIGH),
	C.TOW_PER_LENGTH: ColProps(type=float, highlight=Highlight.HIGH),
	C.POWER_PER_LENGTH: ColProps(type=float, highlight=Highlight.HIGH),
	C.TYPE: ColProps(type=str),
	C.CARGO: ColProps(type=float, generated=False),
	C.BONUS: ColProps(type=str, highlight=Highlight.HIGH, generated=False),
	C.PROFITABILITY: ColProps(type=float, highlight=Highlight.HIGH),
	C.CARGO_PER_LENGTH: ColProps(type=float, highlight=Highlight.HIGH),
	C.PROFIT_PER_LENGTH: ColProps(type=float, highlight=Highlight.HIGH),
	C.CARGO_PER_WT: ColProps(type=float, highlight=Highlight.HIGH),
	C.PROFIT_PER_WT: ColProps(type=float, highlight=Highlight.HIGH),
	C.TP_CARGO: ColProps(type=float, highlight=Highlight.HIGH),
	C.TP_PROFIT: ColProps(type=float, highlight=Highlight.HIGH),
	C.ADJCOST: ColProps(type=float, highlight=Highlight.LOW),
	C.CASH: ColProps(type=float, highlight=Highlight.LOW, generated=False),
	C.COAL: ColProps(type=float, highlight=Highlight.LOW, generated=False),
	C.DIESEL: ColProps(type=float, highlight=Highlight.LOW, generated=False),
	C.ELECTRIC: ColProps(type=float, highlight=Highlight.LOW, generated=False),
	C.TP_ADJCOST: ColProps(type=float, highlight=Highlight.HIGH),
	C.TP_CASH: ColProps(type=float, highlight=Highlight.HIGH),
	C.TP_COAL: ColProps(type=float, highlight=Highlight.HIGH),
	C.TP_DIESEL: ColProps(type=float, highlight=Highlight.HIGH),
	C.TP_ELECTRIC: ColProps(type=float, highlight=Highlight.HIGH),
	C.TPC_ADJCOST: ColProps(type=float, highlight=Highlight.HIGH),
	C.TPP_ADJCOST: ColProps(type=float, highlight=Highlight.HIGH),
	C.TPC_CASH: ColProps(type=float, highlight=Highlight.HIGH),
	C.TPP_CASH: ColProps(type=float, highlight=Highlight.HIGH),
	C.TPC_COAL: ColProps(type=float, highlight=Highlight.HIGH),
	C.TPP_COAL: ColProps(type=float, highlight=Highlight.HIGH),
	C.TPC_DIESEL: ColProps(type=float, highlight=Highlight.HIGH),
	C.TPP_DIESEL: ColProps(type=float, highlight=Highlight.HIGH),
	C.TPC_ELECTRIC: ColProps(type=float, highlight=Highlight.HIGH),
	C.TPP_ELECTRIC: ColProps(type=float, highlight=Highlight.HIGH),
	C.COSTS_RAW: ColProps(type=str, generated=False),
	C.CD6: ColProps(type=float, highlight=Highlight.HIGH),
	C.CD8: ColProps(type=float, highlight=Highlight.HIGH),
	C.COMPOUND_EFFICIENCY: ColProps(type=float, highlight=Highlight.HIGH),
	C.COMPOUND_PROFITABILITY: ColProps(type=float, highlight=Highlight.HIGH),
	C.DENSITY: ColProps(type=float, highlight=Highlight.LOW),
	C.WT_PER_CARGO: ColProps(type=float),
	C.CARGO_UNIT_WT: ColProps(type=float),
}
