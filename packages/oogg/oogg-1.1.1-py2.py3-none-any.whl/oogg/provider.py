from typing import Dict
from urllib.parse import unquote
from urllib.parse import urlparse

from oogg.error import UnknowProvider

_PROVIDERS: Dict[str, str] = {
    "github": "https://{host}/{owner}/{repo}/blob/{branch}/{file}",
    "gitlab": "https://{host}/{owner}/{repo}/-/blob/{branch}/{file}",
    "bitbucket": "https://{host}/{owner}/{repo}/src/{branch}/{file}",
}  # : Hashmap of providers to their url patterns


def format_provider_url(
    platform: str,
    host: str,
    owner: str,
    repo: str,
    branch: str,
    file: str,
) -> str:
    """Format the provider URL

    :param platform: The platform of the provider
    :type platform: str
    :param host: The host of the provider
    :type host: str
    :param owner: The owner of the project
    :type owner: str
    :param repo: The repository of the project
    :type repo: str
    :param branch: The main branch of the project
    :type branch: str
    :param file: The path of the file in the project
    :type file: str

    :return: Return a URL formatted based on the provider.
    :rtype: str
    """
    try:
        provider = _PROVIDERS[platform]

        parsed_filepath = urlparse(unquote(file))

        url = provider.format(
            host=host,
            owner=owner,
            repo=repo,
            branch=branch,
            file=parsed_filepath.path,
        )

        if parsed_filepath.fragment:
            line_number = f"#L{parsed_filepath.fragment}"

            if "-" in parsed_filepath.fragment:
                start, end = tuple(parsed_filepath.fragment.split("-"))
                line_number = f"#L{start}-L{end}"

            url += line_number

        return url
    except (KeyError, ValueError):
        raise UnknowProvider
