FROM python:3.12-alpine
LABEL maintainer="jeremymtoler@gmail.com"

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
VOLUME data/unsorted data/sorted data/logs
COPY apo /apo
WORKDIR /apo
RUN pip install -r requirements.txt

# Run APO
CMD python apo_file_scan.py