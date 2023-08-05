import sys

from zcmds.install.darwin.update import main as darwin_update
from zcmds.install.linux.update import main as linux_update
from zcmds.install.win32.update import main as win32_update


def update() -> None:
    if sys.platform == "darwin":
        darwin_update()
    elif sys.platform == "win32":
        win32_update()
    elif sys.platform == "linux":
        linux_update()
    else:
        raise ValueError("Unhandled platform " + sys.platform)
