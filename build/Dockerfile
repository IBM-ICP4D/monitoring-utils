# set base image (host OS)
FROM python:3.8
RUN mkdir /pvc-monitor
# set the working directory in the container
WORKDIR /pvc-monitor
ADD . /pvc-monitor
# install dependencies
RUN pip install -r requirements.txt
# command to run on container start
CMD [ "python", "./pvc_check.py" ]