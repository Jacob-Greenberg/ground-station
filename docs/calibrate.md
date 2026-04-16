# Calibrating the GS-232 for a G-5500 AZ/EL Controller

## Calibrate Azimuth

1. Run `P45` to set the controller to the 450 degree mode
2. Using the manual controller turn the azimuth to its full left (CCW) end stop. The dial should read 0 degrees
3. Via the computer interface run `O` and hit enter, then press `Y` and hit enter
4. Manually turn the azimuth to its full right (CW) end stop. The dial should read 450 degrees
5. On the computer interface run the `F` command and use a screwdriver to turn the `OUT VOLTAGE ADJ.` (on the back of the GS-5500 above the terminals for the azimuth) potentiometer until the computer reads exactly `AZ=450`

## Calibrate Elevation

1. Using the manual controller turn the elevation to its full down end stop. The dial should read 0 degrees
2. Run `O2` on the computer interface and then hit `Y`
3. Turn the elevation to the full up end stop
4. Run the `F2` command and turn the `OUT VOLTAGE ADJ.` (on the back of the GS-5500 above the terminals for elevation) until it reads exactly `EZ=180`