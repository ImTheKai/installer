FROM python:3.9-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/local/bin/python3 /usr/bin/python3 && \
    pip install --upgrade pip

WORKDIR /opt

RUN git clone https://github.com/EvgeniyPatlan/installer.git

WORKDIR /opt/installer

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /opt/installer/percona_installer && \
    cp /opt/installer/percona_installer /usr/bin/percona_installer

CMD ["percona_installer"]

