FROM ubuntu
ADD collector.py /
ADD requirements.txt /
ADD test_collector.py /


RUN apt-get update
RUN apt-get -y install python3
RUN apt-get install -y python3-pip
RUN pip3 install -r requirements.txt

ENV PORT 2111

EXPOSE 2111

ENTRYPOINT ["python3", "collector.py"]