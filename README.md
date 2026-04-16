# LEOPARDSat Ground Station (Public Edition)

## Getting Started
The groundstation software is written entirely in Python in an effort to make it more maintainable. Instructions provided are for Linux machines, while this software will likely work on Windows it is not written with Windows systems in mind.

### Create a Virtual Environment and Install Dependencies
To start you'll want to create a Python virtual environment (`venv`)
- In the root project directory run `python3 -m venv ./venv`
- If you're using VS Code, `Crtl+Shift+P -> Select Python Interpreter -> ./venv/bin/python` otherwise `./venv/bin/activate` and open a new terminal (the venv should in use now)
- Install dependencies with `pip install -r requirements.txt`

### Configure the `.env` file
Important configuration settings are stored in a `.env` file. This repo comes with a pre-filled out version called `example.env`.
- Make a copy of the example `cp example.env .env`
- Make necessary changes to the settings in the `.env`
- Note: you can also change the system environment variables (handy for use in Docker containers) instead of using a `.env`


### Useful Resources
You can compare pass estimates against these two sites. `n2yo` has 'barely visible' passes that `orbtrack` is sometimes missing
- https://www.n2yo.com/passes/?s=25544#
- https://www.orbtrack.org/#/?satName=ISS%20(ZARYA)