#!/Users/Thibault/Code/random-tests/venv/bin/python

import os
import sys
from dataclasses import dataclass
from functools import cached_property
from typing import Tuple, Union

import requests
from requests import Response

CHANGELOG_PATH = f"github-releases/MOCK_CHANGELOG.md"
GITHUB_USERNAME = "thentges"


def get_github_access_token() -> str:
    return os.getenv("API_ACCESS_TOKEN")


def parse_changelog(changelog_filepath: str = CHANGELOG_PATH) -> Tuple[str, str, str]:
    release_title = ""
    version = ""
    changelog = ""

    with open(changelog_filepath) as f:
        while line := f.readline():
            # first time we encounter H2
            # -> CURRENT release title
            if line.startswith("## ") and not release_title:
                release_title = line[3:]  # remove .md formatting
                version = release_title.split(" ")[0]  # take only the version
                # skip it from the body, since it is in the title
                continue

            # second time we encounter H2
            # -> PREVIOUS release title
            elif line.startswith("## "):
                break

            # skip all H1 headers, the only H1 should be "Changelog"
            elif line.startswith("# "):
                continue

            changelog += line

    if not release_title or not version or not changelog:
        raise Exception("Could not parse changelog")

    return release_title, version, changelog


@dataclass
class GithubReleaseBuilder:
    REPO_NAME: str
    TAG: str
    TITLE: str
    CHANGELOG: str
    ACCESS_TOKEN: str

    USERNAME: str = GITHUB_USERNAME

    @property
    def full_repo(self) -> str:
        return f"{self.USERNAME}/{self.REPO_NAME}"

    @property
    def remote_url(self) -> str:
        return f"{self.full_repo}.git"

    @property
    def headers(self):
        return {"Authorization": f"token {self.ACCESS_TOKEN}"}

    @cached_property
    def already_tagged(self) -> bool:
        res = self._make_github_request("/tags?per_page=15", method="get")
        return self.TAG in [tag["name"] for tag in res.json()]

    @cached_property
    def already_exists(self) -> bool:
        res = self._make_github_request(f"/releases/tags/{self.TAG}", method="get")
        if res.status_code == 404:
            return False

        return True

    def create(self) -> None:
        res = self._make_github_request(
            f"/releases",
            json={
                "tag_name": self.TAG,
                "name": self.TITLE,
                "body": self.CHANGELOG,
            },
            method="post",
        )

        if not res.ok:
            print(_pretty_github_errors_str(res, release_title=self.TITLE))
            exit(1)

    def _make_github_request(self, endpoint, method: str, *args, **kwargs) -> Response:
        return getattr(requests, method)(
            f"https://api.github.com/repos/{self.full_repo}{endpoint}",
            headers=self.headers,
            *args,
            **kwargs,
        )


def _pretty_github_errors_str(
    response: Response, release_title: str
) -> Union[str, dict]:
    try:
        _lines = "\n".join(
            f"  * {err['field']}: {err['code']}" for err in response.json()["errors"]
        )
        return f"Could not create release: {release_title}" + _lines
    except:
        return response.json()


def execute(auto_tag: bool = False):
    # ##### 1. parse environment
    access_token = get_github_access_token()
    if not access_token:
        print(
            "No access token found.\n"
            "Make sure you set the API_ACCESS_TOKEN environment variable."
        )
        exit(1)

    release_title, version, changelog = parse_changelog()

    # prepare the factory
    release_builder = GithubReleaseBuilder(
        # os.getcwd() return the absolute path of the current working directory
        # e.g: the directory from which this script is invoked
        # we take the last part of this part to get the directory name
        REPO_NAME=os.getcwd().split("/")[-1],
        TAG=version,
        TITLE=release_title,
        CHANGELOG=changelog,
        ACCESS_TOKEN=access_token,
    )

    # ##### 2. validation

    # in case the tag does not exist already, do not create release to avoid creating
    # wrong releases in case the version parsing failed for any reason (wrong changelog format, ...)
    # just pass auto_tag=True if you want to remove this security, which is a bit riskier.
    # note that it will check among the last 15 tags only, because of the per_page setting we make.
    if not auto_tag and not release_builder.already_tagged:
        print(
            f"Tag {release_builder.TAG} does not exist on {release_builder.remote_url}\n"
            f"Please make sure you created the tag and reviewed your changelog."
        )
        exit(1)

    if release_builder.already_exists:
        print(
            f"Release for tag {release_builder.TAG} already exists on {release_builder.remote_url}\n"
            f"Please review your changelog."
        )
        exit(1)

    # ##### 3. creation
    release_builder.create()
    print(
        f"To github.com:{release_builder.remote_url}\n"
        f"  * [new release]         {release_builder.TITLE}",
        end="",
    )


def parse_autotag_flag() -> bool:
    try:
        flag = sys.argv[1]
    except IndexError:
        return False

    return flag == "--tag"


execute(auto_tag=parse_autotag_flag())
