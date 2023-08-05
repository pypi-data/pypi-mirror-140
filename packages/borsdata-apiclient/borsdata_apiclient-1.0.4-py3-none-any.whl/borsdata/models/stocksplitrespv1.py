from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .stocksplitv1 import StockSplitV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class StockSplitRespV1:
	stock_split_list: list[StockSplitV1]
