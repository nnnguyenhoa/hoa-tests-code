# get and configure a C image
FROM debian:buster
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    cmake \
    build-essential \
    libboost-all-dev \
    libssl-dev \
    wget \
    zlib1g-dev \
    libc++-7-dev \
    libc++-dev \
    libc++abi-7-dev \
    libc++1 \
    libc++1-7

#Copy our files to the container
COPY . .

#Install python and other programs required to run our app
RUN apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    git


RUN pip3 install -r requirements.txt

RUN git clone https://github.com/tree-sitter/tree-sitter-python vendor/

CMD cd vendor/tree-sitter-python/

RUN git checkout 58f57240834d6b88624e32ad0ab9531d55fb7a5d

CMD cd ../../