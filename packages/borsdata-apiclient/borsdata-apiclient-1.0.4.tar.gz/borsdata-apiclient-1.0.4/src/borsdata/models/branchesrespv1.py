from dataclasses_json import LetterCase, dataclass_json
from dataclasses import dataclass
from .branchv1 import BranchV1


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class BranchesRespV1:
	branches: list[BranchV1]
