# Provide base docker image having python,java,tesseract
FROM base-opencv-java-tesseract-ocr-py38
ENV DEBIAN_FRONTEND=noninteractive
#RUN apt-get update -y


ENV http_proxy=http://10.68.4.62:80
ENV https_proxy=http://10.68.4.62:80
ENV HTTPS_PROXY=http://10.68.4.62:80
ENV HTTP_PROXY=http://10.68.4.62:80

WORKDIR /home
COPY ./MyProgramFiles/ ./MyProgramFiles
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY ./infy_dpp_processor_app/ ./


#creating data dir for container output
RUN mkdir /home/data
RUN	chmod 777 /home/data


# # RUN mkdir /logs
# # RUN	chmod 777 /logs

RUN pip install -r requirements.txt 

RUN pip install pydantic==1.10.18 

ENV http_proxy=''
ENV https_proxy=''
ENV HTTPS_PROXY=''
ENV HTTP_PROXY=''

USER root
WORKDIR $APP_HOME/src

# #ENTRYPOINT ["python", "node1/extract_words.py", "--data_path" "input/dummy_file.txt","--request_id" "R-123"]

# #ENTRYPOINT ["python", "node1/extract_words.py"]
# #ENTRYPOINT ["python"]
# #CMD ["python", "node1/extract_words.py"]
# # CMD ["/bin/bash"]
ENTRYPOINT ["/bin/bash"]