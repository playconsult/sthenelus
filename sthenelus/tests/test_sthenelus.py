import json

from nose.tools import assert_raises, assert_equal

import os
from mock import patch
from mock import MagicMock
from nose import with_setup
from faker import Factory
from sthenelus import QueueClient
import logging

from faker.providers import BaseProvider

class MockProvider(BaseProvider):

    __provider__ = "magicmock"
    __lang__     = "en_GB"

    @classmethod
    def magicmock(cls):
        return MagicMock()


fake = Factory.create()
fake.add_provider(MockProvider)

def setup_func():
    os.environ['QUEUE_NAME'] = fake.pystr()
    logging.getLogger('sthenelus').setLevel(logging.DEBUG)

def teardown_func():
    "tear down test fixtures"

@with_setup(setup_func, teardown_func)
@patch('sthenelus.sthenelus.boto3.resource')
def test_check_environment_raises(mock_resource):
    "test ..."
    # Arrange
    del os.environ['QUEUE_NAME']

    # Act/Assert
    with assert_raises(SystemExit):
        QueueClient()



@with_setup(setup_func, teardown_func)
@patch('sthenelus.sthenelus.boto3.resource')
def test_submit_sends_message(mock_resource):
    "test ..."
    # Arrange

    fake_task_name = fake.pystr()
    fake_params = fake.pylist(10, True, int, str)

    fake_resource = MagicMock()
    fake_queue = MagicMock()
    fake_message_response = MagicMock()
    fake_message_response.get.return_value = MagicMock()
    fake_queue.send_message.return_value = fake_message_response
    fake_resource.get_queue_by_name.return_value = fake_queue

    mock_resource.return_value = fake_resource

    fake_payload = json.dumps({
        'task': fake_task_name,
        'parameters': fake_params
    })

    Q = QueueClient()

    # Act
    Q.submit(fake_task_name, *fake_params)

    # Assert
    fake_queue.send_message.assert_called_once_with(MessageBody=fake_payload)


@with_setup(setup_func, teardown_func)
@patch('sthenelus.QueueClient.log')
@patch('sthenelus.sthenelus.boto3.resource')
def test_submit_failure_logs_error(mock_resource, mock_log):
    "test ..."
    # Arrange

    fake_task_name = fake.pystr()
    fake_params = fake.pylist(10, True, int, str)

    fake_resource = MagicMock()
    fake_queue = MagicMock()
    fake_message_response = MagicMock()
    fake_message_response.get.return_value = None
    fake_queue.send_message.return_value = fake_message_response
    fake_resource.get_queue_by_name.return_value = fake_queue

    mock_resource.return_value = fake_resource

    fake_payload = json.dumps({
        'task': fake_task_name,
        'parameters': fake_params
    })

    Q = QueueClient()

    # Act
    Q.submit(fake_task_name, *fake_params)

    # Assert
    fake_queue.send_message.assert_called_once_with(MessageBody=fake_payload)
    mock_log.exception.assert_called()