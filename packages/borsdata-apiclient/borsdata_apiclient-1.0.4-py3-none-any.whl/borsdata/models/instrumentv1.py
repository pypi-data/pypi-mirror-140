from typing import Optional
from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class InstrumentV1:
    ins_id: int
    name: str
    url_name: str
    instrument: int
    isin: str
    ticker: str
    yahoo: str
    branch_id: Optional[int]
    country_id: int
    market_id: int
    sector_id: Optional[int]
    listing_date: str
