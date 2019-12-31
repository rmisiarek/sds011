import logging
from time import sleep

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


def test_query_data(sensor):
    sensor.set_communication_mode(CommandValue.Passive)
    measurement = sensor.query()
    assert "pm25" in measurement.keys()
    assert "pm10" in measurement.keys()
    assert "time" in measurement.keys()
    logging.info("test_query_data: OK")


def test_device_id(sensor):
    sensor.set_communication_mode(CommandValue.Passive)
    assert sensor.get_device_id() == "0000"
    assert sensor.set_device_id(byte12=12, byte13=13) == "1213"
    assert sensor.device_id == "1213"
    logging.info("test_device_id: OK")


def test_work_mode(sensor):
    assert sensor.set_work_mode(CommandValue.Measuring) == CommandValue.Measuring
    assert sensor.work_mode == CommandValue.Measuring
    sleep(1)
    assert sensor.set_work_mode(CommandValue.Sleeping) == CommandValue.Sleeping
    assert sensor.work_mode == CommandValue.Sleeping
    sleep(1)
    sensor.set_work_mode(CommandValue.Measuring)
    logging.info("test_work_mode: OK")


def test_duty_cycle(sensor):
    assert sensor.set_duty_cycle() == 0
    assert sensor.get_duty_cycle() == 0
    assert sensor.duty_cycle == 0
    sleep(1)
    assert sensor.set_duty_cycle(1) == 1
    assert sensor.get_duty_cycle() == 1
    assert sensor.duty_cycle == 1
    sleep(1)
    assert sensor.set_duty_cycle() == 0
    logging.info("test_duty_cycle: OK")


def test_firmware_version(sensor):
    assert len(sensor.get_firmware_version()) == 6
    logging.info("test_firmware_version: OK")


def run_all_tests(sensor):
    logging.info("SDS011: Started testing ...")
    test_communication_mode(sensor)
    test_query_data(sensor)
    test_device_id(sensor)
    test_work_mode(sensor)
    test_duty_cycle(sensor)
    test_firmware_version(sensor)
    logging.info("SDS011: Tests: OK")
