import os
from pathlib import Path

BASE_PATH = Path(__file__).parent.absolute()
RDP_TEMPLATE = Path(BASE_PATH, "defaults", "Default.rdp")
SUMMONER_FOLDER = Path(Path.home(), ".summoner")
VNC_TEMPLATE = Path(BASE_PATH, "defaults", "Default.rdp")

DEFAULT_INSTANCE = {
    "name": "default",
    "username": os.getlogin(),
    "domain": "create.alt.delete",
    "region": "us-west-1",
    "instance_id": "i-01234567890abcdef",
    "connection_type": "rdp",
}
