# set base image (host OS)
FROM registry.access.redhat.com/ubi8/python-38
# install dependencies
COPY requirements.txt .
COPY scripts/ /tmp/scripts/
RUN pip install -r requirements.txt

USER 1001
# command to run on container start
ENTRYPOINT [ "/tmp/scripts/run_scripts.sh" ]