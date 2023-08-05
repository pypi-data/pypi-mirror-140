from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .kpimetadatav1 import KpiMetadataV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class KpiMetadataRespV1:
	kpi_history_metadatas: list[KpiMetadataV1]
