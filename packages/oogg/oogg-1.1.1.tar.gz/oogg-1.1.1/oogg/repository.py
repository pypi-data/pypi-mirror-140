import subprocess

from giturlparse import parse


class Repository:
    def __init__(self) -> None:
        """Constructor initialization

        :param platform: Name of the platform where the origin remote points
        to.
        :type platform: str
        :param host: The host of the platform the repository points to.
        :type host: str
        :param repo: The name of the repository.
        :type repo: str
        :param owner: The name of the owner of this repository.
        :type owner: str
        :param branch: The current branch in the repository.
        :type branch: str
        """
        self.platform: str = ""
        self.host: str = ""
        self.repo: str = ""
        self.owner: str = ""
        self.branch: str = ""

    def _get_remote_url(self) -> str:
        """Retrieve the remote url using git.

        :return: The remote origin url of the repository.
        :rtype: str
        """
        out = subprocess.run(
            ("git", "config", "--get", "remote.origin.url"),
            capture_output=True,
        )

        return out.stdout.strip().decode("utf-8")

    def _get_remote_branch(self) -> str:
        """Retrieve the current branch using git.

        :return: The current remote branch
        :rtype: str
        """
        out = subprocess.run(
            ("git", "branch", "--show-current"),
            capture_output=True,
        )

        branch_name = out.stdout.strip().decode("utf-8")
        if not branch_name:
            out = subprocess.run(
                ("git", "rev-parse", "HEAD"),
                capture_output=True,
            )

            branch_name = out.stdout.strip().decode("utf-8")
        return branch_name

    def parse(self) -> "Repository":
        """Parse the necessary values for this class

        By calling the private methods inside this class, we shall parse them
        and attribute it to the inner params in the class.

        :return: An instance of the current class.
        :rtype: "Repository"
        """
        origin_url = self._get_remote_url()
        output = parse(origin_url)

        self.platform = output.platform
        self.host = output.host
        self.repo = output.repo
        self.owner = output.owner
        self.branch = self._get_remote_branch()

        return self


repository = Repository().parse()
