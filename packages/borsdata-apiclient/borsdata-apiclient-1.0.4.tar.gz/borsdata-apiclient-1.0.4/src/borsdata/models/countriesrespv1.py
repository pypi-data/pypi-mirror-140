from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .countryv1 import CountryV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class CountriesRespV1:
	countries: list[CountryV1]
