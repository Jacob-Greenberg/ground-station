"""Provides a clean interface for the rotator controller."""

import logging
import time

import serial

logger = logging.getLogger(__name__)


class GS232:
    """Interface for the GS232 rotator controller."""

    # G-5500 is a 450 degree azimuth
    def __init__(
        self,
        port: str,
        degree_mode: int = 360 | 450,
        center_mode: str = "south",
        timeout: float = 5,
    ) -> None:
        """Initialize the GS232 interface."""
        self.gs232 = serial.Serial(
            port=port,
            baudrate=9600,
            rtscts=True,
            timeout=timeout,
        )

        self._azimuth_max = -1
        self._max_tries = 5

        if not self._verify_connection():
            raise ConnectionError("Did not receive input prompt from controller")

        # TODO: fix center mode setting
        # self._verify_connection()
        # self._set_center_mode(center_mode) # skipping this because it's being difficult
        self._verify_connection()
        try:
            self._set_degree_mode(degree_mode)
        except ConnectionError:
            pass
        self._verify_connection()

    def _verify_connection(self, timeout: float = 60) -> bool:
        """Verifies the interface replies with a command prompt.

        This function can be used to ensure the interface is in a 'ready' state.

        :timeout: the time (in seconds) to wait before assuming the interface
                  is offline
        :returns: true if a command prompt was received, false otherwise
        """
        start_time = time.time()
        while self.gs232.readline() != b"?>\r\n":
            self.gs232.write(b"\r\n")
            if time.time() - start_time > timeout:
                return False
        return True

    def _pad_digits(self, num: int) -> str:
        """The interface expects all parameters to be three digits long.

        This function pads numbers with leading zeros as necessary.
        :num: an integer with up to three digits
        :returns: a str with the integer and padding
        :raises: ValueError if num was negative, more than three digits, or not an integer
        """
        if num < 0 or num > 999 or type(num) is not int:
            raise ValueError(
                "Values passed to interface must be integers between 0 and 999",
            )
        digits = len(str(num))
        return (3 - digits) * "0" + str(num)

    # TODO: this does not reliably work
    def _set_center_mode(self, mode: str) -> None:
        """Sets the center (0 degree) mark to be either north or south.

        :mode: 'north' or 'south'
        :raises: ValueError for invalid modes
        :raises: ConnectionError if an invalid response is received
        """
        if mode not in {"south", "north"}:
            raise ValueError("mode must be either north or south")

        self.gs232.write(b"Z\r\n")
        read_line = self.gs232.readline()

        while read_line == b"":
            read_line = self.gs232.readline()

        if read_line == b"S Center" and mode == "south":
            return
        if read_line == b"N Center" and mode == "north":
            return
        self.gs232.write(b"Z\r\n")
        return

    def _set_degree_mode(self, mode: int = 360 | 450) -> None:
        """Tells the GS232 how far the azimuth rotor can turn.

        :mode: The maximum the azimuth rotator can turn
               gs232 supports 360 or 450
        :raises: ValueError when an invalid degree mode is passed
        :raises: ConnectionError if no response is received
        """
        if mode not in {360, 450} or type(mode) is not int:
            raise ValueError("Degree mode must be 360 or 450")
        if mode == 360:
            self.gs232.write(b"P36\r\n")
            read_line = self.gs232.readline()
            if read_line != b"mode 360 Degree\r\n":
                raise ConnectionError("Did not receive response from interface")
            self._azimuth_max = 360
        else:
            self.gs232.write(b"P45\r\n")
            read_line = self.gs232.readline()
            if read_line != b"mode 450 Degree\r\n":
                raise ConnectionError("Did not receive response from interface")
            self._azimuth_max = 450

    def all_stop(self) -> None:
        """Stops all motion on both axis. Does not provide an ack."""
        self.gs232.write(b"S\r\n")

    def azimuth_stop(self) -> None:
        """Stops motion on the azimuth."""
        self.gs232.write(b"A\r\n")

    def elevation_stop(self) -> None:
        """Stops motion of the elevation rotor."""
        self.gs232.write(b"E\r\n")

    def set_azimuth_speed(self, speed: int) -> None:
        """Sets the turning speed of the azimuth rotor.

        :speed: an integer between 1 (slowest) and 4 (fastest)
        :raises: ValueError for invalid parameter
        """
        if speed < 1 or speed > 4 or type(speed) is not int:
            raise ValueError("speed must be an integer between 1 and 4")
        command_str = f"X{speed}\r\n"
        self.gs232.write(command_str.encode("utf-8"))

    def azimuth_turn_to(self, degrees: int) -> None:
        """Turn the azimuth rotor to a specific angle.

        :degrees: an integer degree to turn to
        :raises: ValueError if degree is too large or small, or not an integer
        """
        if degrees < 0 or degrees > self._azimuth_max or type(degrees) is not int:
            msg = f"degrees must be an integer between 0 and {self._azimuth_max}"
            raise ValueError(
                msg,
            )
        command_str = f"M{self._pad_digits(degrees)}\r\n"
        self.gs232.write(command_str.encode("utf-8"))

    def azimuth_elevation_turn_to(self, degrees_az: int, degrees_el: int) -> None:
        """Simultaneously turn the azimuth and elevation rotors to a specific angle.

        :degrees_az: an integer degree to turn the azimuth to
        :degrees_el: an integer degree to turn the elevation to
        :raises: ValueError if either degree value is invalid

        *note*: executes `start_timed_command`
        """
        if (
            degrees_az < 0
            or degrees_az > self._azimuth_max
            or type(degrees_az) is not int
        ):
            msg = f"degrees_az must be an integer between 0 and {self._azimuth_max}"

            raise ValueError(
                msg,
            )
        if degrees_el < 0 or degrees_el > 180 or type(degrees_el) is not int:
            raise ValueError("degrees_el must be an integer between 0 and 180")
        command_str = (
            f"W{self._pad_digits(degrees_az)} {self._pad_digits(degrees_el)}\r\n"
        )
        self.gs232.write(command_str.encode("utf-8"))
        self.start_timed_command()  # required otherwise the elevation will not move

    def start_timed_command(
        self,
    ) -> None:
        """Used in conjunction with the timed interval commands to trigger them.

        :raises: ValueError if num_steps is unset
        """
        self.gs232.write(b"T\r\n")

    def get_azimuth_elevation(self) -> tuple[int, int]:
        """Returns the current azimuth and elevation as integers.

        :returns: (ax, el)
        """
        self.gs232.write(b"C2\r\n")
        line = self.gs232.readline().decode("utf-8")
        while not line.startswith("AZ"):
            line = self.gs232.readline().decode(
                "utf-8",
            )  # TODO: this uses the last line received. All commands should leave the console in a default state
        az = int(line[3:6])
        el = int(line[11:14])
        return (az, el)

    def get_direction_value(self):
        pass

    def azimuth_sequence(self, step_time: int, angle_list: list[int]) -> None:
        """Rotate about the azimuth through a sequence of angles.

        Immediately turns towards the first angle, moves through
        remaining angles when `start_timed_command` is called
        :step_time: the delay (in seconds) between each step
        :angle_list: a list of angles to turn to, up to 3800 angles
        :raises: ValueError for invalid parameters
        *note* long passes can take a while to write to the gs232
        """
        if type(step_time) is not int or step_time < 0 or step_time > 999:
            raise ValueError("step_time must be an integer between 0 and 999")

        # TODO: error handling
        if len(angle_list) < 2 or len(angle_list) > 3800:
            raise ValueError(
                "Angle list must contain at least 2 but no more than 3800 elements",
            )

        command_str = f"M{self._pad_digits(step_time)}"
        for angle in angle_list:
            command_str = command_str + f" {self._pad_digits(angle)}"
        command_str = command_str + "\r\n"
        self.gs232.write(command_str.encode("utf-8"))

    def azimuth_elevation_sequence(
        self,
        step_time: int,
        angle_pairs: list[list[int], list[int]],
    ) -> None:
        """Rotate to a sequence of azimuth/elevation pairs.

        Immediately turns towards the first pair, moves through
        remaining angles when `start_timed_command` is called
        :step_time: the delay (in seconds) between each step
        :angle_pairs: a list of tuples with the (azimuth, elevation) in degrees,
                      at least 2 pairs, up to 1900
        :raises: ValueError for invalid parameters
        *note* long passes can take a while to write to the gs232
        """
        if type(step_time) is not int or step_time < 0 or step_time > 999:
            raise ValueError("step_time must be an integer between 0 and 999")

        # TODO: error handling
        if len(angle_pairs) < 2 or len(angle_pairs) > 1900:
            raise ValueError(
                "Angle list must contain at least 2 elements, with no more than 1900 pairs",
            )

        command_str = f"W{self._pad_digits(step_time)}"
        for pair in angle_pairs:
            az = pair[0]
            el = pair[1]
            command_str = (
                command_str + f" {self._pad_digits(az)} {self._pad_digits(el)}"
            )
        command_str = command_str + "\r\n"
        self.gs232.write(command_str.encode("utf-8"))
