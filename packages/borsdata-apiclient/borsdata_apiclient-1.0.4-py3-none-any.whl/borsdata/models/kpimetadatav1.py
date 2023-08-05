from typing import Optional
from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class KpiMetadataV1:
	kpi_id: int
	name_sv: str
	name_en: str
	format: Optional[str]
	is_string: bool
