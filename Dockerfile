
FROM ubuntu:latest

ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get -y update
RUN apt-get install python2 curl -y
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py
RUN python2 get-pip.py
RUN apt-get install -y python2-dev build-essential nginx

COPY . /app
WORKDIR /app

expose 3000

RUN pip install -r requirements.txt
ENV /usr/lib/python2.7 python
ENV FLASK_APP=browse.py

CMD ["python2", "-m", "flask", "run", "--host=0.0.0.0", "-p 3000"]

