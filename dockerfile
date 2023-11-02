FROM python:3.12-alpine
# Install ExifTool
RUN apk add --no-cache perl make
COPY Image-ExifTool-12.69.tar.gz .
RUN tar -zxvf Image-ExifTool-12.69.tar.gz \
	&& cd Image-ExifTool-12.69 \
	&& perl Makefile.PL \
	&& make test \
	&& make install \
	&& cd .. \
	&& rm -rf Image-ExifTool-12.69.tar.gz
# Setup APO
VOLUME unsorted sorted
COPY apo /apo
WORKDIR /apo
RUN pip install -r requirements.txt
# ENV ALERT_THRESHOLD \
#     MAX_LOGS \
#     WAIT_TIME \
#     USE_EMAIL \
#     EMAIL_ADDRESS \
#     USE_SLACK \
#     SLACK_OAUTH \
#     SLACK_CHANNEL
RUN python apo_setup.py
# Run APO
CMD python apo_file_scan.py