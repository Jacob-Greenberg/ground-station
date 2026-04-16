"""Satellite pass predictor."""

import json
import logging
from datetime import datetime, timedelta

import requests
from skyfield.api import EarthSatellite, Time, Timescale, load, wgs84

from .telemetry import Telemetry

logger = logging.getLogger(__name__)


class Predictor:
    """Generates azimuth/elevation pairs for a given pass."""

    def __init__(
        self,
        ground_station_lat: float,
        ground_station_long: float,
        ground_station_elevation: float,
        satellite_id: int,
        telemetry: Telemetry,
    ) -> None:
        """Initialize the predictor."""
        self.observer = wgs84.latlon(ground_station_lat, ground_station_long)
        self.time_scale = load.timescale()
        self.telemetry = telemetry
        self.satellite_id = satellite_id
        self.satellite: EarthSatellite = None
        self.update_satellite_telemetry()

    def update_satellite_telemetry(self) -> None:
        """Helper to update the satellite object to use the latest TLE."""
        tle = self.telemetry.get_tle(self.satellite_id)
        self.satellite = EarthSatellite(tle[1], tle[2], tle[0], self.time_scale)

    def _unify_time(self, time: datetime | Time = None) -> Time:
        """Helper to ensure all times are the correct type."""
        if time is None:
            return self.time_scale.now()
        if type(time) is datetime:
            return self.time_scale.from_datetime(time)
        if type(time) is Time:
            return time
        raise ValueError(f"Unsupported time type {type(time)}")

    def get_satellite_events(
        self,
        start_time: Time,
        end_time: Time,
        degrees_over_horizon: float = 15,
    ) -> list:
        """Returns all the instances a satellite will cross the horizon between two times.

        Returns a list of lists, first with the stack of events,
        then with the individual events and times
        """
        # 0 rises above horizon
        # 1 culmination (can be more than one)
        # 2 sinks below horizon
        times, events = self.satellite.find_events(
            self.observer,
            start_time,
            end_time,
            degrees_over_horizon,
        )

        event_list = []
        event_stack = []

        for ti, event in zip(times, events, strict=True):
            event_stack.append([ti, event])
            if event == 2:
                event_list.append(event_stack)
                event_stack = []
        return event_list

    def calculate_az_el_pairs_for_pass(
        self,
        start_time: Time,
        end_time: Time,
        time_step: int,
    ) -> list:
        """Calculate the azimuth/elevation pairs for a given pass."""
        num_steps = int((end_time - start_time).total_seconds() // time_step)
        step_duration = (end_time - start_time) / num_steps

        # print(start_time.utc_datetime())
        # print(end_time.utc_datetime())
        # print(num_steps)
        # print(step_duration)

        difference = self.satellite - self.observer
        pairs = []
        for i in range(num_steps + 1):
            time_at_step = start_time + i * step_duration
            topocentric = difference.at(self._unify_time(time_at_step))
            alt, az, distance = topocentric.altaz()
            pairs.append([int(az.degrees), int(alt.degrees)])
        return pairs

    def convert_360_pairs_to_450(self, pairs: list) -> list:
        """Allows the predictor to use the full 450 degrees of the rotator.

        Our azimuth rotator is able to spin 450 degrees the additional
        90 degrees gives the rotator some wiggle room for passes which
        overshoot the limit.

        The predictor has no way of knowing this however so this function
        turns sequences that would ordinarily overshoot in a 360 degree
        system to 450 degrees. It's worth pointing out that this doesn't
        totally prevent overshooting
        """
        for index, pair in enumerate(pairs):
            az = pair[0]
            increase_index = 0

            if index > 0 and az < 10 and pairs[index - 1][0] > 350:
                while (
                    index + increase_index < len(pairs)
                    and pairs[index + increase_index][0] <= 90
                ):
                    new_az = pairs[index + increase_index][0] + 360
                    if new_az > 450:  # sanity check
                        break
                    pairs[index + increase_index][0] = new_az
                    increase_index = increase_index + 1

            index = increase_index + index
        return pairs

    def pass_has_gap(self, pairs: list) -> bool:
        """Checks if a pass will have a transmission gap.

        As mentioned in `convert_360_pairs_to_450` there is potential for a pass
        to require the rotator overshoot its bounds. When the rotator overshoots it
        must swing all the way back around. During this move it is likely (especially
        for passes occurring low on the horizon) the satellite will leave the lobe
        of the antenna interrupting data transfer

        This function returns true if a pass has a gap (jump from ~360/~450 to 0)
        """
        for i in range(len(pairs)):
            if i > 0 and pairs[i][0] < 350 and pairs[i - 1][0] > 350:
                return True
        return False
