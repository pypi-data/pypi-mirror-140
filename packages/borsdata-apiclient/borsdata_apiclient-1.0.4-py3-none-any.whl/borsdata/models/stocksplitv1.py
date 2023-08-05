from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class StockSplitV1:
	instrument_id: int
	split_type: str
	ratio: str
	split_date: str
