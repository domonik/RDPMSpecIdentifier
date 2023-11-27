import os
import yaml


VISDIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(os.path.dirname(VISDIR), "dashConfig.yaml")
assert os.path.exists(CONFIG_FILE), "Config file does not exist"
with open(CONFIG_FILE, "r") as handle:
    CONFIG = yaml.load(handle, Loader=yaml.SafeLoader)

EXTERNEL_CONFIG_FILE = os.getenv('RDPMS_CONFIG_FILE')
if EXTERNEL_CONFIG_FILE:
    with open(EXTERNEL_CONFIG_FILE, "r") as handle:
        EXTERNEL_CONFIG = yaml.load(handle, Loader=yaml.SafeLoader)

    CONFIG.update(EXTERNEL_CONFIG)


if CONFIG["display"]["mode"]:
    DISPLAY = True
    DISPLAY_FILE = CONFIG["display"]["file"]
    if not os.path.exists(DISPLAY_FILE):
        raise ValueError(f"Running in Display Mode but cannot find the file to display:\n Expected File {DISPLAY_FILE}")
else:
    DISPLAY = False
    DISPLAY_FILE = None
DISABLED = DISPLAY
MAX_KERNEL_SLIDER = CONFIG["kernel"]["max"]


BOOTSH5 = "col-12 justify-content-center px-0"
BOOTSROW = "row  px-4 px-md-4 py-1"