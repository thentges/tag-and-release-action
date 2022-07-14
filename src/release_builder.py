from dataclasses import dataclass
from functools import cached_property
from typing import Union

import requests
from requests import Response

from src.cfg import GITHUB_ACCESS_TOKEN


@dataclass
class GithubReleaseBuilder:
    REPO_NAME: str
    TAG: str
    TITLE: str
    CHANGELOG: str

    @property
    def remote_url(self) -> str:
        return f"{self.REPO_NAME}.git"

    @property
    def headers(self):
        return {"Authorization": f"token {GITHUB_ACCESS_TOKEN}"}

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
            f"https://api.github.com/repos/{self.REPO_NAME}{endpoint}",
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
