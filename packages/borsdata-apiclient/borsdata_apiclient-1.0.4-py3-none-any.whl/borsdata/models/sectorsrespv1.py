from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .sectorv1 import SectorV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class SectorsRespV1:
	sectors: list[SectorV1]
