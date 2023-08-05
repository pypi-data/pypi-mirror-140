from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .kpihistoryv1 import KpiHistoryV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class KpisHistoryRespV1:
	kpi_id: int
	report_time: str
	price_value: str
	values: list[KpiHistoryV1]
