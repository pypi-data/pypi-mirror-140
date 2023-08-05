from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .kpisummaryvaluev1 import KpiSummaryValueV1

"""This is the only API with PASCAL KpiId instead of CAMEL kpiId"""


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass(frozen=True)
class KpiSummaryGroupV1:
    kpi_id: int
    values: list[KpiSummaryValueV1]
