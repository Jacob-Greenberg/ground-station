# API Specifications


## Controlling the Ground Station


### Parking
When the ground station is not in use the it will 'park' itself. By default it will park facing due North. If a wind direction API is accessible it will face the antennas pointing towards the wind to reduce the wind load.

### Hard Limits
The rotator will not allow itself to be pointed below the horizon. It will ignore commands which request



## Controlling the Ground Station

### Exposes /update-tle
TBI: Updates the ground station's prediction TLE, allows autonomous usage

### Exposes /add-pass | json
Adds a new pass to the internal queue. Returns an error if the start time has already passed
```js
"uuid":<unique id>, // optional, randomly generated if not included
"start-time": <UTC-Start Time>,
"start-az": degrees,
"start-el": degrees,
"peak-time": [<UTC>, <UTC>],
"end-time": <UTC>
```

### Exposes /list-queue | json
Returns a list of queued passes, may be empty


### Exposes /update-pass | json
Updates an existing pass' details

### Exposes /stop | request
Reciving this request causes the station to halt all movement and transmission

## Managing the Ground Station

### Exposes /list-data | request -> json
Returns the current data files stored on disk. Stored as packet IDs

### Exposes /get-data | request -> bits
Returns a specific packet as a binary file.

### Exposes /uptime | request -> json
Returns the current system uptime

### Exposes /restart | request
Soft restarts the entire ground station

## Sending Transmissions

### Expects /uplink | websocket
When a pass starts, the ground station will attempt to connect to this endpoint.
Bytes sent to this endpoint are sent to the satellite

### Expects /downlink | websocket
When a pass starts, the ground tation will attempt to connect to this endpoint.
Bytes recieved by the station are added to this websocket


## Debugging
Debug features are enabled via a .env variable, they should be left off when not in use

### Exposes /aim | json
Turns towards a given azimuth, elevation, or both
```js
// turn only azimuth
{"az": 123}

// turn only elevation
{"el" : 90}

// turn both 
{
	"az":123,
	"el":90
}
```

### Exposes /calibrate | request
Station calibrates on its own, this forces it







