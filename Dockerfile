# Use an official Python runtime as a parent image
FROM python:3.12

WORKDIR /finesse_scraper

COPY requirements.txt .

COPY . . 

RUN pip install -r requirements.txt

ENV DEBIAN_FRONTEND=noninteractive

ENTRYPOINT [ "bash" ]

# Run additional setup commands
# RUN echo "Setting up the container..." \
#     && cd /tmp \
#     && apt update \
#     && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb\
#     && apt install ./google-chrome-stable_current_amd64.deb -y \
#     && cd ../finesse_scraper