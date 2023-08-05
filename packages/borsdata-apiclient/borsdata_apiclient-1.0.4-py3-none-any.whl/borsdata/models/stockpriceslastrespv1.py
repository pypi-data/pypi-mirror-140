from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .stockpricefullv1 import StockPriceFullV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class StockPricesLastRespV1:
	stock_prices_list: list[StockPriceFullV1]
