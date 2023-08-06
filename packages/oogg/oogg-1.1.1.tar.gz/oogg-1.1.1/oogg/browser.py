import subprocess
import sys

from rich import print


def open_with_browser(url: str) -> int:
    """Open the given pathfile in the browser

    This method will used the favorite browser of the user by actually calling
    them using `xdg-open` on unix, `open` on MacOS and `start` on win32.

    :param url: The URL to open in the browser.
    :type url: str
    :return: The return code of the subprocess call
    :rtype: int
    """
    cmd = "xdg-open"
    if sys.platform == "win32":
        cmd = "start"
    elif sys.platform == "darwin":
        cmd = "open"
    try:
        out = subprocess.run(
            (cmd, url),
            capture_output=True,
        )

        print(
            "[green]Hooray! We have successfully opened your file in your"
            "prefered browser.[/green]",
        )
        return out.returncode
    except (subprocess.CalledProcessError) as exception:
        print(
            "[red]Oh no! There was an error trying to open your browser "
            ":(.[/red]",
        )
        return exception.returncode
