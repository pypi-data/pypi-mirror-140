from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .marketv1 import MarketV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class MarketsRespV1:
	markets: list[MarketV1]
