from typing import Optional
from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class MarketV1:
    id: int
    name: str
    country_id: int
    is_index: bool
    exchange_name: Optional[str]
