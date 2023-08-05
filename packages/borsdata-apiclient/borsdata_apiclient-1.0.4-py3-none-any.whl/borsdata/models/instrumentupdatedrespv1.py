from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .instrumentupdatedv1 import InstrumentUpdatedV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class InstrumentUpdatedRespV1:
	instruments: list[InstrumentUpdatedV1]
