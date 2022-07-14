import os
import sys
from typing import Tuple

from src.cfg import CHANGELOG_PATH, LOCAL_REPO_OWNER, ONLINE_REPO_NAME
from src.release_builder import GithubReleaseBuilder


def get_local_repository_name():
    # os.getcwd() return the absolute path of the current working directory
    # e.g: the directory from which this script is invoked
    # we take the last part of this part to get the directory name.
    return f"{LOCAL_REPO_OWNER}/{os.getcwd().split('/')[-1]}"


def parse_changelog() -> Tuple[str, str, str]:
    release_title = ""
    version = ""
    changelog = ""

    with open(CHANGELOG_PATH) as f:
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


def execute(auto_tag: bool = False):
    release_title, version, changelog = parse_changelog()

    release_builder = GithubReleaseBuilder(
        REPO_NAME=ONLINE_REPO_NAME or get_local_repository_name(),
        TAG=version,
        TITLE=release_title,
        CHANGELOG=changelog,
    )

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
