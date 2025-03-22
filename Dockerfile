FROM postgres:15

ENV POSTGRES_DB=filestore
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=secretpassword

COPY init.sql /docker-entrypoint-initdb.d/ 