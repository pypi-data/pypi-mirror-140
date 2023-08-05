from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .reportv1 import ReportV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ReportsCompoundRespV1:
	instrument: int
	reports_year: list[ReportV1]
	reports_quarter: list[ReportV1]
	reports_r12: list[ReportV1]
