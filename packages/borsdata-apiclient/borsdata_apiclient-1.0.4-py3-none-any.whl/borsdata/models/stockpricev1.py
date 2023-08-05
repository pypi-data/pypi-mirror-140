from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class StockPriceV1:
	d: str
	h: float
	l: float
	c: float
	o: float
	v: int
