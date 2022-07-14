# tag-and-release-action

GitHub Action running a python script inside a docker container.

When the github-action detects a commit starting with `chg: :bookmark:`, and containing the text `preparing v`, it will automatically tag it, and create a release.

It will parse a CHANGELOG.md file with a format such as:

```markdown
# Changelog

## v1.0.1 (xxxx-xx-xx)

### Changes
...

## v1.0.0 (xxxx-xx-xx)

### Changes
...

```

And include it in the release's body.

That way, to release a new version of your application, just prepare your changelog accordingly, and commit with a message such as `chg: :bookmark: preparing v1.0.1`.

## Usage as a GitHub action

In your .github/workflows directory, create a `auto-tag-and-release.yml` file, and copy paste the following code:

```yaml
name: auto-tag-and-release

on:
  push:
    branches: [ "dev" ]


  workflow_dispatch:

jobs:
  tag-or-release:
    uses: thentges/tag-and-release-action/.github/workflows/auto-tag-and-release.yml@v1
    secrets:
      API_ACCESS_TOKEN: ${{ secrets.API_ACCESS_TOKEN }}

```

You will need to define a secret in your github repository or organization, API_ACCESS_TOKEN, with all the `repo` scopes.
- https://github.com/settings/tokens/new

## Local usage

### Installation

- Create a GitHub API token here: https://github.com/settings/tokens/new
- Clone this repository
- Copy the file `local-entrypoint.py` to a new `auto-tag-and-release.py` file
- Change the permissions of this newly created file
```bash
sudo chmod 777 github-releases/src/auto-tag-and-release.py.py
```
- In this file, replace the first shebang line, with the path to a working python >= 3.8 environment with requests installed
- Add the path to this repository to your PATH
```bash
export PATH=$PATH:<path-to-repo-on-your-machine>
```
- Add the following environment variables to your .bashrc, or every-time you want to run the command
```bash
export CHANGELOG_PATH=CHANGELOG.md
export LOCAL_REPO_OWNER=<name of the owner of the repository you are working in> # can be overridden anytime
```
- Add the following function to your .bashrc/.zshrc
```bash
git() {
    if [[ $@ == "auto-release" ]] ; then
        command auto-tag-and-release.py
    elif [[ $@ == "auto-release --tag" ]]; then
        command auto-tag-and-release.py --tag
    else
        command git "$@"
    fi
}
```

### Usage

Now that everything is installed you have access to the `git auto-release` command.

By default, git auto-release will require the tag to exist on your remote repository, and just parse your local CHANGELOG.md file to create a release.
You can change this behavior by passing the `--tag` flag, that will also create a tag when running the command.

