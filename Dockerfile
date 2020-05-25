FROM python:3.8.3-slim-buster

LABEL maintainer="Yann Defretin <yann@defret.in"

# Install dependencies for everything
COPY ./requirements.txt /allocine/requirements.txt
RUN /bin/bash -c "pip3 install --no-cache-dir -r /allocine/requirements.txt"

# copy static code to the image
COPY . /allocine

WORKDIR /allocine

CMD ["scraper.py"]
ENTRYPOINT ["python3"]
