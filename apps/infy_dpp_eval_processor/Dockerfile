# Provide base docker image having python,java,tesseract
FROM base-opencv-java-tesseract-ocr-py38
ENV DEBIAN_FRONTEND=noninteractive
#RUN apt-get update -y

ENV http_proxy=''
ENV https_proxy=''
ENV HTTPS_PROXY=''
ENV HTTP_PROXY=''


WORKDIR /home
COPY ./MyProgramFiles/ ./MyProgramFiles
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY ./infy_dpp_eval_processor_app/ ./


#creating data dir for container output
RUN mkdir /home/data
RUN	chmod 777 /home/data


RUN pip install -r requirements.txt  --no-cache-dir 


ENV http_proxy=''
ENV https_proxy=''
ENV HTTPS_PROXY=''
ENV HTTP_PROXY=''

USER root
WORKDIR $APP_HOME/src


ENTRYPOINT ["/bin/bash"]