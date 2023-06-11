FROM arm32v7/python:3.10-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN \
    apt-get update && \
    apt-get -y install libffi-dev libsodium-dev ffmpeg libnacl-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./bb3.py" ]