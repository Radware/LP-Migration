
FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential nginx

COPY . /app
WORKDIR /app

expose 3000

RUN pip install -r requirements.txt
ENV FLASK_APP=browse.py

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "-p 3000"] 
