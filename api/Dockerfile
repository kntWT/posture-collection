FROM python:3.10
 
USER root
COPY ssl /ssl

WORKDIR /app

COPY api .
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libgl1-mesa-dev
RUN pip install -U pip
# RUN pip install -r pytorch-openpose/requirements.txt
RUN pip install -r requirements.txt

CMD python main.py
