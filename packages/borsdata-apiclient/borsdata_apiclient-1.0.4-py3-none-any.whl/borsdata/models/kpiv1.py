from typing import Optional
from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class KpiV1:
	i: int
	n: Optional[float]
	s: Optional[str]
