# set base image (host OS)
FROM registry.access.redhat.com/ubi8/python-38
# install dependencies

COPY scripts /scripts
COPY run_scripts.sh .
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /scripts

USER 1001
# command to run on container start
ENTRYPOINT [ "./run_scripts.sh" ]