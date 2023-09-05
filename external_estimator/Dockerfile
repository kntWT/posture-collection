FROM python:3.10

USER root

WORKDIR /app

COPY . .
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libgl1-mesa-dev
RUN pip install -U pip
RUN pip install -r requirements.txt

CMD python human_posture_analysis_camera.py