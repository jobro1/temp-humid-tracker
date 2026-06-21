FROM eclipse-temurin:11-jre

ARG PDI_VERSION=9.4.0.0-343
ARG PDI_MAJOR=9.4
ARG PDI_ZIP=pdi-ce-${PDI_VERSION}.zip
ARG PDI_URL=https://github.com/ambientelivre/legacy-pentaho-ce/releases/download/pdi-ce-9.4.0.0-343/${PDI_ZIP}

WORKDIR /app

RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*

RUN curl -L -o /tmp/${PDI_ZIP} "${PDI_URL}" \
    && unzip -q /tmp/${PDI_ZIP} -d /opt/pentaho \
    && rm /tmp/${PDI_ZIP}

RUN chmod +x /opt/pentaho/data-integration/*.sh

RUN curl -L -o /opt/pentaho/data-integration/lib/postgresql-jdbc.jar \
    "https://repo1.maven.org/maven2/org/postgresql/postgresql/42.6.0/postgresql-42.6.0.jar"

COPY kafka_consumer.ktr stream.ktr entrypoint.sh /app/ktr/

RUN chmod +x /app/ktr/entrypoint.sh

ENV KETTLE_HOME=/app
ENV PENTAHO_DI_JAVA_OPTIONS="-Xms512m -Xmx1g"

ENTRYPOINT ["/app/ktr/entrypoint.sh"]
CMD ["-file=/app/ktr/kafka_consumer.ktr", "-level=Basic"]
