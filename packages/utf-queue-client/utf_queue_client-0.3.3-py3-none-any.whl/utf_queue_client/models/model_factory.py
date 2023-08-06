from . import (
    SqaTestResultRecord,
    SqaTestSessionMetadata,
    BaseModelWithValidation,
)
from typing import Type, Dict, TypeVar

T = TypeVar("T")


"""
Maps a model type to a set of defaults
"""
DEFAULTS_MAP: Dict[Type[BaseModelWithValidation], dict] = {
    SqaTestResultRecord: dict(
        testCaseId="",
        status="failed",
        testResult="failed",
        testResultType="FEATURE",
        sessionId="",
        testStartTime=0,
        testStopTime=0,
        testDurationSec=0,
    ),
    SqaTestSessionMetadata: dict(
        sessionId="", sessionStartTime=0, status="", stackName=""
    ),
}


def create_model_with_defaults(model_type: Type[T], **kwargs) -> T:
    if model_type in DEFAULTS_MAP:
        return model_type(DEFAULTS_MAP[model_type], **kwargs)

    return model_type(**kwargs)
