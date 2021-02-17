FROM ubuntu
ADD recommender.py /
ADD requirements.txt /
ADD test_recommender.py /

RUN apt-get update
RUN apt-get -y install python3
RUN apt-get install -y python3-pip
RUN pip3 install -r requirements.txt

ENV PORT 2211

EXPOSE 2211

ENTRYPOINT ["python3", "recommender.py"]