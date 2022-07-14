FROM alpine:3.8

COPY script.py.sh /script.py
RUN pip install requests

COMMAND python script.py