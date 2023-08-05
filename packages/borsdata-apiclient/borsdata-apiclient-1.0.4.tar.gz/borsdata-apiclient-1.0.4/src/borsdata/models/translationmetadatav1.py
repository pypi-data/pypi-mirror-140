from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class TranslationMetadataV1:
	name_sv: str
	name_en: str
	translation_key: str
