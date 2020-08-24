FROM python:3.8.5-alpine3.12

ADD . /test-reader
RUN pip install /test-reader
RUN rm -rf /test-reader

ENV APP_NAME=app
ENV YAML_CONFIG_PATH=/app/test_reader_config.yml
ENV RESULT_DIR=/app/
ENV ROOT_FILE_PATH=/app
ENV PUBLISHER=csv 

ENTRYPOINT cd /app; test-reader-start;
