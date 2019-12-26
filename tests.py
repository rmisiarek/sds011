import logging

from command import *

logging.getLogger(__name__)


def test_communication_mode(sensor):
    # active mode:
    sensor.set_communication_mode(CommandValue.Active)
    assert sensor.communication_mode == CommandValue.Active
    assert sensor.get_communication_mode() == CommandValue.Active
    assert sensor.communication_mode == CommandValue.Active
    # passive mode:
    sensor.set_communication_mode(CommandValue.Passive)
    assert sensor.communication_mode == CommandValue.Passive
    assert sensor.get_communication_mode() == CommandValue.Passive
    assert sensor.communication_mode == CommandValue.Passive
    logging.info("test_communication_mode: OK")


def run_all_tests(sensor):
    test_communication_mode(sensor)
