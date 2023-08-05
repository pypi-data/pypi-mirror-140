from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .reportv1 import ReportV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ReportsRespV1:
	instrument: int
	reports: list[ReportV1]
