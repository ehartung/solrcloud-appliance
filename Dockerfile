FROM registry.opensource.zalan.do/stups/openjdk:8-53

RUN apt-get update && apt-get install -y wget python3 unzip python3-pip

RUN wget -q -O - http://www.mirrorservice.org/sites/ftp.apache.org/lucene/solr/6.3.0/solr-6.3.0.tgz | tar -xzf - -C /opt \
    && mv /opt/solr-6.3.0 /opt/solr
RUN chmod -R 777 /opt/solr

RUN wget -q -O /opt/jolokia-jvm-1.3.2-agent.jar "http://search.maven.org/remotecontent?filepath=org/jolokia/jolokia-jvm/1.3.2/jolokia-jvm-1.3.2-agent.jar"

ADD solr.xml solr.xml
ADD zoo.cfg zoo.cfg
ADD log4j.properties /opt/solr/server/resources/log4j.properties

ADD configs /opt/solr/configs

ADD scripts /opt/solr/scripts
RUN chmod 777 /opt/solr/scripts/*

RUN pip3 install --upgrade -r /opt/solr/scripts/requirements.txt

ADD startup.sh startup.sh
RUN chmod 777 startup.sh

ADD startup-local.sh startup-local.sh
RUN chmod 777 startup-local.sh

ADD scm-source.json scm-source.json

EXPOSE 8983 8778

WORKDIR /opt/solr/

CMD ["/bin/bash", "-c", "/startup.sh"]
