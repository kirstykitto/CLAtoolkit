FROM ubuntu:14.04
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Install dependencies
RUN \
  apt-get update && \
  apt-get -y install build-essential && \
  apt-get -y install python-pip && \
  apt-get -y install libxml2-dev libxslt1-dev python-dev && \
  apt-get -y install liblapack3 libgfortran3 libumfpack5.6.2 && \
  apt-get -y install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose && \
  apt-get -y install unzip && \
  apt-get -y install libpq-dev python-dev && \
  apt-get -y install libpq-dev && \
  apt-get -y install gfortran libblas-dev liblapack-dev && \
  apt-get -y install libfreetype6-dev libpng12-dev libqhull-dev libfreetype6 && \
  apt-get -y install pkg-config

# Set work directories
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install requirements
COPY requirements.txt /usr/src/app
RUN pip install -r requirements.txt

# Copy files to Dockerfile
COPY ./clatoolkit_project /usr/src/app
