
FROM ubuntu
RUN apt-get update

#Downloading tools
RUN apt-get install -y git python-pip wget unzip

#Downloading dependencies
RUN apt-get install -y libxml2-dev libxslt-dev lib32z1-dev python2.7-dev libssl-dev

#other dependencies
RUN apt-get install -y python-dev libxslt1-dev libsasl2-dev libsqlite3-dev libldap2-dev libffi-dev
RUN pip install ftp://xmlsoft.org/libxml2/python/libxml2-python-2.6.9.tar.gz

# TODO(JMC): We need to build a bunch of docker images for different tempest tags
ENV THE_TEMPEST_CODE_URL https://github.com/openstack/tempest/archive/stable/havana.zip

RUN wget $THE_TEMPEST_CODE_URL  -O tempest.zip
RUN unzip tempest.zip
RUN mv /tempest-stable* /tempest

#Tempest dependencies
RUN pip install -r /tempest/tools/test-requires || true
RUN pip install -r /tempest/requirements.txt || true
RUN pip install -r /tempest/test-requirements.txt || true

ADD . /refstack
RUN pip install -r /refstack/requirements.txt

# Run the scripts, expecting lots of ENV variables
CMD python /refstack/refstack/tools/execute_test.py
