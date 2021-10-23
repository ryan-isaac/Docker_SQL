FROM python:3.8-slim-buster

MAINTAINER  Ryan Isaac, isaac-ca@outlook.com

WORKDIR /usr/src/app

COPY requirements.txt ./

ADD financial_data_analysis.py .

RUN apt-get update

RUN pip3 install -r requirements.txt

RUN mkdir ./output

COPY . .

CMD [ "python", "./financial_data_analysis.py" ]
