from utf_queue_client.models import (
    SqaTestResultRecord,
    SqaTestSessionMetadata,
    SqaTestEvent,
    QueueMessage,
    ArtifactUploadRequest,
    ArtifactMetadata,
    ArtifactBuildMetadata,
)
from utf_queue_client.exceptions import SchemaValidationError, ValidationError
from utf_queue_client.models.model_factory import (
    create_model_with_defaults,
    DEFAULTS_MAP,
)
import json
import pytest


def test_model_factory_no_args_valid():
    # these types support empty initializer
    types_supporting_defaults_or_no_args = [SqaTestSessionMetadata, SqaTestResultRecord]
    for model_type in types_supporting_defaults_or_no_args:
        create_model_with_defaults(model_type)


def test_model_factory_no_args_invalid():
    # these types do not support creation with empty initializer
    types_requiring_args = [QueueMessage, SqaTestEvent]
    for model_type in types_requiring_args:
        with pytest.raises(ValidationError):
            create_model_with_defaults(model_type)


def test_sqa_test_results_record_model_creation():
    valid_defaults = DEFAULTS_MAP[SqaTestResultRecord]

    # kwarg creation
    model = SqaTestResultRecord(**{**valid_defaults, "invalid_attr": True})
    assert model.testCaseId == valid_defaults["testCaseId"]
    assert "invalid_attr" not in model.dict()

    # dict creation
    model = SqaTestResultRecord({**valid_defaults, "invalid_attr": True})
    assert model.testCaseId == valid_defaults["testCaseId"]
    assert "invalid_attr" not in model.dict()

    with pytest.raises(ValidationError):
        SqaTestResultRecord(dict(invalid_attr=True))


def test_sqa_test_results_record_schema_validation():
    valid_defaults = DEFAULTS_MAP[SqaTestResultRecord]

    model = SqaTestResultRecord(valid_defaults)
    model.validate_schema()
    model.status = "passed"
    model.validate_schema()

    model.testCaseId = 4
    with pytest.raises(SchemaValidationError):
        model.validate_schema()

    model.status = "PASS"
    with pytest.raises(SchemaValidationError):
        model.validate_schema()


def test_sqa_test_event_creation():
    with pytest.raises(ValidationError):
        _ = SqaTestEvent(eventType="TEST_RESULT", invalid_attr=True)


def test_sqa_test_event_schema_validation():
    model = SqaTestEvent(
        eventType="TEST_RESULT",
        testResult=SqaTestResultRecord(DEFAULTS_MAP[SqaTestResultRecord]),
        testSessionMetadata=SqaTestSessionMetadata(
            DEFAULTS_MAP[SqaTestSessionMetadata]
        ),
    )
    model.validate_schema()


def test_artifact_upload_request():
    model = ArtifactUploadRequest(
        name="foop",
        extension=".py",
        metadata={},
        base64Content="6",
        validateMetadata=False,
    )
    model.validate_schema()
    with pytest.raises(SchemaValidationError):
        model.base64Content = 6
        model.validate_schema()


def test_deserialize_queue_message():
    message = {
        "payload": {
            "eventType": "SESSION_COMPLETE",
            "testSessionMetadata": {
                "sessionId": "22022309-0143-8042-08f5-a121823f92ab",
                "sessionStartTime": 1645628503.804208,
                "status": "IN PROGRESS",
                "jobType": "NA",
                "releaseName": "NA",
                "SDKBranchName": "NA",
                "stackName": "NA",
                "SDKBuildNum": -1,
                "SDKURL": "NA",
                "studioBuildURL": "NA",
                "jenkinsServerName": "NA",
                "jenkinsRunNum": -1,
                "jenkinsJobName": "NA",
                "jenkinsTestResultsUrl": "NA",
                "jobBuildNum": -1,
                "studioBranchName": "NA",
                "studioBuildNum": -1,
                "parentBuildNum": -1,
                "parentBuildURL": "NA",
            },
        },
        "recordType": "TEST_EVENT",
        "timestamp": 1645628949.187504,
    }
    queue_message = QueueMessage(message)
    if queue_message.recordType == "TEST_EVENT":
        _ = SqaTestEvent(queue_message.payload.dict())
