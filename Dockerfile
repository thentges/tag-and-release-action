FROM python:3.8-alpine

# 1. add needed files to run the action
ADD src /src

# 2. add online / github-actions entrypoints
ADD docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ADD online-entrypoint.py /entrypoint.py

# 3. install dependencies
RUN pip install requests

# 4. export required environment variables
ENV CHANGELOG_PATH /github/workspace/CHANGELOG.md

ARG INPUT_API_ACCESS_TOKEN
ENV INPUT_API_ACCESS_TOKEN $INPUT_API_ACCESS_TOKEN

ARG INPUT_REPOSITORY_NAME
ENV INPUT_REPOSITORY_NAME $INPUT_REPOSITORY_NAME

# 5. execute command
ENTRYPOINT ["/entrypoint.sh"]
