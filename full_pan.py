from gs232_wrapper.gs232_wrapper import GS232
from time import sleep

rotator = GS232('/dev/ttyUSB0', 450, "south", timeout=1)
rotator._azimuth_max = 450
az, el = rotator.get_azimuth_elevation()
print(az, el)
rotator.set_azimuth_speed(1)

rotator.azimuth_turn_to(0)
rotator.azimuth_elevation_turn_to(0, 0)
#sleep(30)
#rotator.azimuth_elevation_turn_to(90, 90)