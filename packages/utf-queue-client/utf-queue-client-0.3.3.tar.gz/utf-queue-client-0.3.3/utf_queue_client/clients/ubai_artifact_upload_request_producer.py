import os.path

from .base_producer import BlockingProducer
from ..models import ArtifactUploadRequest, ArtifactMetadata, ArtifactBuildMetadata
from ..models import QueueMessage
from socket import gethostname
from datetime import datetime
import base64
import os

__all__ = [
    "UbaiArtifactUploadRequestProducer",
    "LocalUbaiArtifactUploadRequestProducer",
]


class UbaiArtifactUploadRequestProducer:
    def __init__(self, url=None, producer_app_id: str = None):
        self.queue_name = "ubai_artifact_request"
        self.__client = BlockingProducer(url, producer_app_id)
        self.__client.queue_declare(queue=self.queue_name, durable=True)

    def upload_artifact(
        self, artifact_file: str, metadata: dict, validate_metadata: bool=True
    ):
        if validate_metadata:
            required_properties = ["branch", "stack", "build_number", "target"]
            missing_keys = [
                key
                for key in required_properties
                if key not in metadata
            ]
            if len(missing_keys):
                raise RuntimeError(
                    f"metadata is missing the following required properties: {','.join(missing_keys)}"
                )

        name, extension = os.path.splitext(os.path.split(artifact_file)[1])
        with open(artifact_file, "rb") as f:
            contents = f.read()
            base64_content = base64.b64encode(contents).decode("utf-8")
        artifact_request = ArtifactUploadRequest(
            name=name,
            extension=extension,
            base64Content=base64_content,
            metadata=ArtifactMetadata(**metadata),
            validateMetadata=validate_metadata,
        )
        self.publish_artifact_upload_request(artifact_request)

    def publish_artifact_upload_request(self, artifact_request: ArtifactUploadRequest):
        queue_message = QueueMessage(
            payload=artifact_request,
            recordType="ARTIFACT_UPLOAD_REQUEST",
            timestamp=datetime.now().timestamp(),
        )
        queue_message.validate_schema()

        self.__client.publish(
            exchange="",
            routing_key=self.queue_name,
            payload=queue_message.as_dict(),
            persistent=True,
        )


class LocalUbaiArtifactUploadRequestProducer(UbaiArtifactUploadRequestProducer):
    def __init__(self):
        super().__init__(
            "amqp://guest:guest@localhost:5672/%2f",
            f"LocalSqaTestResultProducer at {gethostname()}",
        )
