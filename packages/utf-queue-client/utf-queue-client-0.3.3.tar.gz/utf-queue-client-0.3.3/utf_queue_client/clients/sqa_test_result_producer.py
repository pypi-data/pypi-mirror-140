import os

from .base_producer import BlockingProducer, ConnectionError
from ..models import SqaTestResultRecord
from ..models import SqaTestSessionMetadata
from ..models import SqaTestEvent
from ..models import QueueMessage
from . import Loggable
from socket import gethostname
from datetime import datetime
from abc import ABC, abstractmethod

__all__ = [
    "SqaTestResultProducer",
    "LocalSqaTestResultProducer",
    "ConnectionError",
    "SqaTestResultProducerFactory",
]


class BaseSqaTestResultProducer(ABC):
    @abstractmethod
    def publish_test_event(self, test_event: SqaTestEvent):
        pass

    @abstractmethod
    def publish_test_session_event(
        self, event_type: str, test_session_metadata: SqaTestSessionMetadata
    ):
        pass

    @abstractmethod
    def publish_test_results(
        self,
        test_result_record: SqaTestResultRecord,
        test_session_metadata: SqaTestSessionMetadata,
    ):
        pass


class SqaTestResultProducer(BaseSqaTestResultProducer):
    SESSION_START_EVENT_TYPE = "SESSION_START"
    TEST_RESULT_EVENT_TYPE = "TEST_RESULT"
    SESSION_COMPLETE_EVENT_TYPE = "SESSION_COMPLETE"

    def __init__(self, url=None, producer_app_id: str = None):
        self.queue_name = "sqa_test_results"
        self.__client = BlockingProducer(url, producer_app_id)
        self.__client.queue_declare(queue=self.queue_name, durable=True)

    def publish_test_event(self, test_event: SqaTestEvent):
        queue_message = QueueMessage(
            payload=test_event,
            recordType="TEST_EVENT",
            timestamp=datetime.now().timestamp(),
        )
        queue_message.validate_schema()

        self.__client.publish(
            exchange="",
            routing_key=self.queue_name,
            payload=queue_message.as_dict(),
            persistent=True,
        )

    def publish_test_session_event(
        self, event_type: str, test_session_metadata: SqaTestSessionMetadata
    ):
        test_event = SqaTestEvent(
            eventType=event_type,
            testSessionMetadata=test_session_metadata,
        )
        self.publish_test_event(test_event)

    def publish_test_results(
        self,
        test_result_record: SqaTestResultRecord,
        test_session_metadata: SqaTestSessionMetadata,
    ):
        test_event = SqaTestEvent(
            eventType=self.TEST_RESULT_EVENT_TYPE,
            testResult=test_result_record,
            testSessionMetadata=test_session_metadata,
        )
        self.publish_test_event(test_event)


class LocalSqaTestResultProducer(SqaTestResultProducer):
    def __init__(self):
        super().__init__(
            "amqp://guest:guest@localhost:5672/%2f",
            f"LocalSqaTestResultProducer at {gethostname()}",
        )


class DummySqaTestResultProducer(BaseSqaTestResultProducer):
    def publish_test_event(self, test_event: SqaTestEvent):  # noqa
        pass

    def publish_test_session_event(
        self, event_type: str, test_session_metadata: SqaTestSessionMetadata
    ):  # noqa
        pass

    def publish_test_results(
        self,
        test_result_record: SqaTestResultRecord,
        test_session_metadata: SqaTestSessionMetadata,
    ):  # noqa
        pass


class SqaTestResultProducerFactory(Loggable):
    @classmethod
    def create_producer(cls, raise_on_connection_error=False):
        try:
            if os.environ.get("UTF_QUEUE_SERVER_URL") is not None:
                return SqaTestResultProducer()
            else:
                return LocalSqaTestResultProducer()
        except ConnectionError as e:
            cls.logger.warning(f"Unable to connect to queue server: {repr(e)}")
            if raise_on_connection_error:
                raise
            return DummySqaTestResultProducer()
