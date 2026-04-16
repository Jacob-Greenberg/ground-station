"""The main entrypoint for the program."""

import logging
import os
from datetime import UTC, datetime, timedelta
from time import sleep

from dotenv import load_dotenv

from gs232_wrapper.gs232_wrapper import GS232
from pass_prediction.satellite_predictor import Predictor
from pass_prediction.telemetry import Telemetry

logger = logging.getLogger(__name__)


def get_events(predictor: Predictor) -> list[tuple[datetime, datetime, datetime]]:
    """Retrieves events (passes) for the next 24 hours.

    Returns a list of tuples, each with the start time,
    peak time, and end time of a pass.
    """
    t0 = predictor.time_scale.now()
    t1 = predictor.time_scale.now() + timedelta(days=1)
    events = predictor.get_satellite_events(t0, t1)

    event_list = []

    for event in events:
        start_time = event[0][0].utc_datetime()
        peak_time = event[1][0].utc_datetime()
        end_time = event[-1][0].utc_datetime()

        event_list.append((start_time, peak_time, end_time))

    return event_list


if __name__ == "__main__":
    # Load a .env file for standalone use
    # this call fails gracefully so you can
    # also specify env vars in the docker compose
    load_dotenv()
    OBSERVER_LATITUDE = os.getenv("OBSERVER_LATITUDE")
    OBSERVER_LONGITUDE = os.getenv("OBSERVER_LONGITUDE")
    OBSERVER_ELEVATION = os.getenv("OBSERVER_ELEVATION")
    SECONDS_BETWEEN_STEPS = os.getenv("SECONDS_BETWEEN_STEPS")
    GS232_SERIAL_DEVICE = os.getenv("GS232_SERIAL_DEVICE")
    AZIMUTH_DEGREE_MODE = os.getenv("AZIMUTH_DEGREE_MODE")
    CENTER_MODE = os.getenv("CENTER_MODE")
    CACHE_TIMEOUT = os.getenv("CACHE_TIMEOUT")
    CACHE_DIR = os.getenv("CACHE_DIR")
    LEOPARDSAT_CATALOG_NUMBER = os.getenv("LEOPARDSAT_CATALOG_NUMBER")

    logging.basicConfig(filename="gs.log", level=logging.DEBUG)

    logger.info("[...] Configuring Rotator")
    rotator = GS232(
        GS232_SERIAL_DEVICE,
        int(AZIMUTH_DEGREE_MODE),
        CENTER_MODE,
        timeout=1,
    )
    logger.info("[...] Establishing Telemetry")
    telemetry = Telemetry(
        float(CACHE_TIMEOUT),
        CACHE_DIR,
    )
    logger.info("[...] Priming Predictor")
    predictor = Predictor(
        float(OBSERVER_LATITUDE),
        float(OBSERVER_LONGITUDE),
        float(OBSERVER_ELEVATION),
        int(LEOPARDSAT_CATALOG_NUMBER),
        telemetry,
    )

    while True:
        events = get_events(predictor)
        for event in events:
            start = event[0]
            end = event[-1]
            pairs = predictor.calculate_az_el_pairs_for_pass(
                start,
                end,
                int(SECONDS_BETWEEN_STEPS),
            )
            pairs = predictor.convert_360_pairs_to_450(pairs)
            logger.info("[...] Sending sequence to controller")
            rotator.azimuth_elevation_sequence(int(SECONDS_BETWEEN_STEPS), pairs)
            logger.info("[...] Sequence received")
            duration = end - start
            delta = start.timestamp() - datetime.now(UTC).timestamp()
            logger.info(
                f"[...] Next pass at {start} for {duration}"
                f"waiting for {delta} seconds until next pass",
            )
            sleep(delta)
            rotator.start_timed_command()
        sleep(60)
