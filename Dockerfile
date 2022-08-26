# start by pulling the python image
FROM python:3.8-slim
ARG port

USER root

# switch working directory
WORKDIR /app

# copy the requirements file into the image
COPY requirements.txt requirements.txt
# copy every content from the local file to the image
COPY ./application .

# Set and update linux OS packages
ENV PORT=$port
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils \
    && apt-get -y install curl \
    && apt-get install libgomp1

# Configure the container to run in an executed manner
RUN chgrp -R 0 . \
    && chmod -R g=u . \
    && pip install pip --upgrade \
    && pip install -r requirements.txt

EXPOSE $PORT
ENV START_THREADING=True

CMD exec gunicorn application:app --bind 0.0.0.0:$PORT --workers=4