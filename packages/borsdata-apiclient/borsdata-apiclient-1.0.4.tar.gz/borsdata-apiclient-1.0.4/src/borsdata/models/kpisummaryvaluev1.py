from typing import Optional
from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class KpiSummaryValueV1:
	y: int
	p: int
	v: Optional[float]
