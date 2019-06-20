FROM developmentseed/geolambda:1.1.0-python36

WORKDIR task
COPY requirements.txt .
COPY build_thumbnails.py .

RUN pip install -r requirements.txt
