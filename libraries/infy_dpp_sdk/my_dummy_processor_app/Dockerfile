FROM python:3.11
ENV DEBIAN_FRONTEND=noninteractive
#RUN apt-get update -y

ENV http_proxy=''
ENV https_proxy=''
ENV HTTPS_PROXY=''
ENV HTTP_PROXY=''

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

#creating data dir for output
# RUN mkdir /data
# RUN	chmod 777 /data

# RUN mkdir /data/pipeline
# RUN	chmod 777 /data/pipeline

# RUN mkdir /logs
# RUN	chmod 777 /logs

RUN pip install -r requirements.txt

ENV http_proxy=''
ENV https_proxy=''
ENV HTTPS_PROXY=''
ENV HTTP_PROXY=''

USER root
WORKDIR $APP_HOME/src

#ENTRYPOINT ["python", "node1/extract_words.py", "--data_path" "input/dummy_file.txt","--request_id" "R-123"]

#ENTRYPOINT ["python", "node1/extract_words.py"]
#ENTRYPOINT ["python"]
#CMD ["python", "node1/extract_words.py"]
# CMD ["/bin/bash"]
ENTRYPOINT ["/bin/bash"]