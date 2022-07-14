import os

# Shared config
GITHUB_ACCESS_TOKEN = os.getenv("INPUT_API_ACCESS_TOKEN")
CHANGELOG_PATH = os.getenv("CHANGELOG_PATH")

# GitHub actions only
ONLINE_REPO_NAME = os.getenv("INPUT_REPOSITORY_NAME")

# Local-use only
LOCAL_REPO_OWNER = os.getenv("LOCAL_REPO_OWNER")
