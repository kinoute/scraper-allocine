FROM python:3.8.3-slim-buster

LABEL maintainer="Yann Defretin <yann@defret.in"

# Common dependencies
RUN apt-get update -qq \
  && DEBIAN_FRONTEND=noninteractive apt-get install -yq \
    --no-install-recommends \
    gcc=4:8.3.0-1 \
    libpq-dev=11.7-0+deb10u1 \
    libevent-dev \
    python3-dev \
  && apt-get clean \
  && rm -rf /var/cache/apt/archives/* \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
  && truncate -s 0 /var/log/*log

# Install dependencies for everything
COPY ./requirements.txt /allocine/requirements.txt
RUN /bin/bash -c "pip3 install --no-cache-dir -r /allocine/requirements.txt"

# copy static code to the image
COPY . /allocine

WORKDIR /allocine

CMD ["scraper.py"]
ENTRYPOINT ["python3"]
