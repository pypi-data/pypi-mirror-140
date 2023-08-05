from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .stockpricev1 import StockPriceV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class StockPricesRespV1:
	instrument: int
	stock_prices_list: list[StockPriceV1]
