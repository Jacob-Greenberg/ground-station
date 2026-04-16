from gs232_wrapper.gs232_wrapper import gs232
from pass_prediction.telemetry import Telemetry
from pass_prediction.satellite_predictor import Predictor
from datetime import datetime, timedelta
from time import sleep

rotator = gs232('/dev/ttyUSB0', 450, "south", timeout=1)
az, el = rotator.get_azimuth_elevation()
print(az, el)
rotator.set_azimuth_speed(4)

OBSERVER_LAT = 39.1031
OBSERVER_LON = -84.5120

SECONDS_BETWEEN_STEPS = 1

ut = Telemetry()

pred = Predictor(OBSERVER_LAT, OBSERVER_LON, 0, 25544, ut) # ISS (ZARYA)
t0 = pred.time_scale.now()
t1 = pred.time_scale.now() + timedelta(days=1)
events = pred.get_satellite_events(t0, t1)
event_list = events[0]
start_time = event_list[0][0]
print(start_time.utc_datetime())
end_time = event_list[-1][0]
duration = end_time.utc_datetime() - start_time.utc_datetime()
print(duration)
pairs = pred.calculate_az_el_pairs_for_pass(event_list, SECONDS_BETWEEN_STEPS)
pairs = pred.convert_360_pairs_to_450(pairs)

rotator.azimuth_elevation_sequence(SECONDS_BETWEEN_STEPS, pairs)
input(f"Press any key to start timed command... (estimated runtime: ~{len(pairs) * SECONDS_BETWEEN_STEPS} seconds)")
rotator.start_timed_command(True, len(pairs))


#rotator.azimuth_elevation_turn_to(az, 90)
#rotator.azimuth_sequence(10, [0, 90, 180, 270, 360, 450])
#rotator.azimuth_elevation_sequence(15, [[0, 0], [10, 10], [20, 20], [30, 30]])
#input("Press any key to start timed command...")
#rotator.start_timed_command()

#rotator.azimuth_turn_to(0)
#sleep(10)
#rotator.azimuth_turn_to(90)
#sleep(10)
#rotator.azimuth_turn_to(0)

