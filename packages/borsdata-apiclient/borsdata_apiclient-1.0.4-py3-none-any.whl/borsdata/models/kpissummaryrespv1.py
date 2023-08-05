from typing import Optional
from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .kpisummarygroupv1 import KpiSummaryGroupV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class KpisSummaryRespV1:
    kpi_id: int
    report_time: Optional[str]
    price_value: Optional[str]
    kpis: list[KpiSummaryGroupV1]
