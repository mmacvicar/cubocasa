"""Constants for Cubo Casa."""
# Base component constants
NAME = "Cubo Casa"
DOMAIN = "cubocasa"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1"

ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/mmacvicar/cubo-casa/issues"

# Icons
ICON = "mdi:format-quote-close"

# Platforms
LOCK = "lock"
PLATFORMS = [LOCK]

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
