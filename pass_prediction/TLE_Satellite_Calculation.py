"""This is a reference file with some example code. It is not part
of the actual project and should not be developed in.
"""

import requests
from skyfield.api import EarthSatellite, Topos, load


# Make an hourly cron job & Save to file to pull
def fetch_tle(catnr, format="TLE"):
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={catnr}&FORMAT={format}"
    response = requests.get(url)
    response.raise_for_status()

    if format == "TLE":
        return response.text.strip().split("\n")
    raise ValueError("Unsupported format")


def get_satellite_azimuth_elevation_distance(
    tle_data, observer_lat, observer_lon, observer_elevation_m=0, format="TLE"
):
    ts = load.timescale()

    if format == "TLE":
        satellite = EarthSatellite(tle_data[1], tle_data[2], tle_data[0], ts)
    else:
        raise ValueError("Unsupported format for computation")

    t = ts.now()
    observer = Topos(
        latitude_degrees=observer_lat,
        longitude_degrees=observer_lon,
        elevation_m=observer_elevation_m,
    )
    observer_astrometric = (satellite - observer).at(t)
    alt, az, d = observer_astrometric.altaz()
    return alt, az, d


def is_satellite_visible(
    tle_data, observer_lat, observer_lon, observer_elevation_m=0, format="TLE"
):

    alt, az, d = get_satellite_azimuth_elevation_distance(
        tle_data, observer_lat, observer_lon, observer_elevation_m=0, format="TLE"
    )
    return alt.degrees > 15


def find_next_overhead_pass(
    tle_data, observer_lat, observer_lon, observer_elevation_m=0, format="TLE"
):
    ts = load.timescale()

    if format == "TLE":
        satellite = EarthSatellite(tle_data[1], tle_data[2], tle_data[0], ts)
    else:
        raise ValueError("Unsupported format for computation")

    observer = Topos(
        latitude_degrees=observer_lat,
        longitude_degrees=observer_lon,
        elevation_m=observer_elevation_m,
    )
    t = ts.now()

    while True:
        observer_astrometric = (satellite - observer).at(t)
        alt, az, d = observer_astrometric.altaz()

        if alt.degrees > 15:
            return t.utc_datetime()

        t = ts.utc(
            t.utc_datetime().year,
            t.utc_datetime().month,
            t.utc_datetime().day,
            t.utc_datetime().hour,
            t.utc_datetime().minute + 1,
        )


def calculate_rate_of_doppler(
    freq_carrier: float, height: float, velocity: float, distance: float
) -> float:
    """Calculate the rate of change of the doppler effect

    Args:
        freq_carrier (float): frequency of communication
        height (float): distance (y coordinate) of observer to satellite
        velocity (float): speed of satiellite #I have a suspicion this could be a constant
        distance (float): distance (x coordinate) of observer to satellite

    Returns:
        float: The derivative of the doppler effect

    """
    c = 3e8  # speed of light

    return (velocity * freq_carrier * height**2) / (
        c * (distance**2 + height**2) ** (3 / 2)
    )


# I am not sure if this function is necessary, but I wanted to put it here before I forgot. The fetch_tle function seems to get data, but I wasn't sure if it did the derivative
# if the tle function only gives long/lat coords, we might have to expand this function to calculate height and distance

# Example usage:
tle = fetch_tle(25544, format="TLE")
observer_lat = 39.1031  # Example: Cincinnati, OH
observer_lon = -84.5120

visible = is_satellite_visible(tle, observer_lat, observer_lon, format="TLE")
print("Satellite is visible:", visible)

overhead_pass = find_next_overhead_pass(tle, observer_lat, observer_lon, format="TLE")
print("Next overhead pass at:", overhead_pass)

# TODO: Get az/el pair at the time the pass begins and aim the antenna at it
# TODO: Calculate az/el pairs and load them into controller
