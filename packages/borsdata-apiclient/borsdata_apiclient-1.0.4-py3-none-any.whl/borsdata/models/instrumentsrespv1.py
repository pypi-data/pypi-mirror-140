from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .instrumentv1 import InstrumentV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class InstrumentsRespV1:
	instruments: list[InstrumentV1]
