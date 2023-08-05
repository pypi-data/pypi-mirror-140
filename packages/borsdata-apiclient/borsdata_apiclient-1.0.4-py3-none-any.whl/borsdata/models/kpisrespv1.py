from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .kpiv1 import KpiV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class KpisRespV1:
	kpi_id: int
	group: str
	calculation: str
	value: KpiV1
