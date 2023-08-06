import argparse

from rich import print

from oogg.browser import open_with_browser
from oogg.error import UnknowProvider
from oogg.provider import format_provider_url
from oogg.repository import repository


def create_parser() -> argparse.Namespace:
    """Create the argument parser for the application.

    :return: The namespace with the parsed args
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--owner",
        help="Username associated with the repository.",
        default=repository.owner,
    )
    parser.add_argument(
        "--repository",
        help="Name of the repository.",
        default=repository.repo,
    )
    parser.add_argument(
        "--host",
        help="The host of the provider.",
        default=repository.host,
    )
    parser.add_argument(
        "--branch",
        help="Branch of the repository.",
        default=repository.branch,
    )
    parser.add_argument(
        "filepath",
        help="The desired path of the file (Can include the line number with a"
        "#<number> or #<from-number>-<to-number>)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entrypoint for the oogg application.

    :return: int as a return code
    :rtype: int
    """
    args = create_parser()

    try:
        url = format_provider_url(
            platform=repository.platform,
            host=args.host,
            owner=args.owner,
            repo=args.repository,
            branch=args.branch,
            file=args.filepath,
        )
    except (UnknowProvider):
        print(
            f"[red]Failed to parse the {repository.platform} provider.[/red]",
        )
        return 1
    return open_with_browser(url=url)
