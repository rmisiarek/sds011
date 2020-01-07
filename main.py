import logging
from sys import exit

import db
from sds011 import SDS011
from tests import run_all_tests

logging.getLogger(__name__)

sensor = SDS011("/dev/ttyUSB0")


if sensor:
    run_all_tests(sensor)
    sensor.set_duty_cycle(1)

    connection = db.create_connection(db.DB_NAME)
    if connection is None:
        logging.error(f"DB [{db.DB_NAME}]: cannot create the database connection!")

    with connection:
        db.create_table(conn=connection, create_table_sql=db.SQL_CREATE_TABLE)

        while True:
            try:
                r = sensor.sender.read()
                if sensor.sender.is_valid_active_response(r):
                    data = sensor.extract_pm_values(r)
                    row = (data["pm10"], data["pm25"], data["time"])
                    db.insert_row(conn=connection, row=row)
            except KeyboardInterrupt:
                exit("\nBye!")
