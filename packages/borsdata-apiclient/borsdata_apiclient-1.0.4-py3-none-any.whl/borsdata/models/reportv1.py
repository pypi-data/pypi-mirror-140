from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ReportV1:
	year: int
	period: int
	revenues: float
	gross__income: float
	operating__income: float
	profit__before__tax: float
	profit__to__equity__holders: float
	earnings__per__share: float
	number__of__shares: float
	dividend: float
	intangible__assets: float
	tangible__assets: float
	financial__assets: float
	non__current__assets: float
	cash__and__equivalents: float
	current__assets: float
	total__assets: float
	total__equity: float
	non__current__liabilities: float
	current__liabilities: float
	total__liabilities__and__equity: float
	net__debt: float
	cash__flow__from__operating__activities: float
	cash__flow__from__investing__activities: float
	cash__flow__from__financing__activities: float
	cash__flow__for__the__year: float
	free__cash__flow: float
	stock__price__average: float
	stock__price__high: float
	stock__price__low: float
	report__start__date: str
	report__end__date: str
	broken__fiscal__year: bool
	currency: str
	currency__ratio: float
	net__sales: float
	report__date: str
