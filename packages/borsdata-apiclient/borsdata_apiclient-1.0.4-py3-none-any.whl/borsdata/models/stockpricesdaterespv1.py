from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .stockpricedatev1 import StockPriceDateV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class StockPricesDateRespV1:
	stock_prices_list: list[StockPriceDateV1]
