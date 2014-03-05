
FROM ubuntu
RUN apt-get update

#Downloading tools
RUN apt-get install -y git python-pip wget unzip

#Downloading dependencies
RUN apt-get install -y libxml2-dev libxslt-dev lib32z1-dev python2.7-dev libssl-dev

#other dependencies
RUN apt-get install -y python-dev libxslt1-dev libsasl2-dev libsqlite3-dev libldap2-dev libffi-dev
RUN pip install ftp://xmlsoft.org/libxml2/python/libxml2-python-2.6.9.tar.gz

ENV TEST_ID 1000
ENV API_SERVER_ADDRESS 0.0.0.0:8000
ENV THE_TEMPEST_CODE_URL https://github.com/openstack/tempest/archive/stable/havana.zip

RUN wget $THE_TEMPEST_CODE_URL  -O tempest.zip
RUN unzip tempest.zip
RUN mv /tempest-stable* /tempest

#Tempest dependencies
RUN pip install -r /tempest/tools/test-requires || true
RUN pip install -r /tempest/requirements.txt || true
RUN pip install -r /tempest/test-requirements.txt || true


#Download the Python script to the container.  This script will be used to prepare
# the test environment, run tempest tests and upload the test results to RefStack
# RUN wget http://${API_SERVER_ADDRESS}/get-script -O execute_test.py

ADD ./refstack/tools/execute_test.py /execute_test.py 
ADD ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Run the script
RUN python /execute_test.py ${API_SERVER_ADDRESS} ${TEST_ID} 'THE_CONF_JSON'
RUN echo "done"
