from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .reportmetadatav1 import ReportMetadataV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ReportMetadataRespV1:
	report_metadatas: list[ReportMetadataV1]
