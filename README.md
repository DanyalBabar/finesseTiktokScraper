# Docker Setup

### Run Dockerfile:
1. `docker build -t finesse-img .`
2. `docker run -it -d -v finesse_scrape/data --name finesse-script finesse-img`
3. `docker exec -it finesse-script /bin/bash`

### Within the Docker container, install Google Chrome:
    cd /tmp \
        && apt update \
        && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb\
        && apt install ./google-chrome-stable_current_amd64.deb -y \
        && cd ../finesse_scraper

### Run scraper script:
`python Scraper.py`

Scraped TikTok posts will print as they are scraped and will appear in `postLinks.csv`.

</br>

# Non-Docker Setup
If the Docker setup does not work, there are only two requirements to run `Scraper.py` and have it scrape files for you:
- Latest version of Google Chrome installed
- `pip install selenium selenium-stealth`
