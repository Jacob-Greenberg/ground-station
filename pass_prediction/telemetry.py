"""The class handles telemetry requests to celestrak.

It caches the results for a certain amount of time to
be respectful to celestrak.
"""

import logging
import os
import time
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


class Telemetry:
    """Respectfully requests satellite telemetry from Celestrak.

    Data is cached for future use and automatically updated when it is stale
    """

    def __init__(
        self,
        cache_timeout: float = 24 * 60 * 60,
        data_dir: str = "./data",
    ) -> None:
        """Initialize the telemetry class.

        :cache_timeout: the length of time (in seconds) before
        a cached entry is too old and should be updated

        *IMPORTANT* celestrak will temporarily ban IPs that make too many requests so
        this should be about every day at most
        :data_dir: the path to store cached objects
        """
        self.data_dir = data_dir
        self.cache_timeout = cache_timeout

    def get_tle(self, catnr: int) -> list[str]:
        """Respectfully get the TLE of a given item.

        :catnr: the catalog number
        :returns: the tle
        """
        return self._check_cache(catnr)

    def _check_cache(self, catnr: int) -> list[str]:
        """Check if we already have this item cached, pull a new one if it's expired.

        :catnr: the catalog number
        :returns: the tle
        """
        if Path(f"{self.data_dir}/{catnr}.tle").is_file():
            with Path(f"{self.data_dir}/{catnr}.tle").open("r") as tle_file:
                pulled_at = float(tle_file.readline())
                if time.time() - pulled_at < self.cache_timeout:
                    logger.info("Cache hit!")
                    return tle_file.readlines()
        logger.info("Cache miss :(")
        tle = self._fetch_tle(catnr)
        self._cache_tle(catnr, tle)
        return tle

    def _fetch_tle(self, catnr: int) -> list[str]:
        """Reach out to celestrak of a tle.

        :catnr: the catalog number
        :returns: the tle as a list of strings
        """
        url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={catnr}&FORMAT=TLE"
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        return response.text.strip().split("\n")

    def _cache_tle(self, catnr: int, tle: list[str]) -> None:
        """Cache the TLE so we don't need to check celestrak.

        :catnr: the catalog number (really just the file name)
        :tle: the tle as a list of strings
        """
        with Path(f"{self.data_dir}/{catnr}.tle").open("w") as tle_file:
            tle_file.write(f"{time.time()}\n")  # The time stamp the cache was made at
            tle_file.writelines(f"{line}\n" for line in tle)
