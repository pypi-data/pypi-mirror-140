from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .translationmetadatav1 import TranslationMetadataV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class TranslationMetadataRespV1:
	translation_metadatas: list[TranslationMetadataV1]
