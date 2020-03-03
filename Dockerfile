FROM obcon/ubuntu-python3.6:latest
COPY port_proxy /root/port_proxy
WORKDIR /root/port_proxy
RUN apt-get update
RUN apt-get -y install python3-pip
RUN pip3 install -r requirements.md -i https://pypi.doubanio.com/simple/  --trusted-host pypi.doubanio.com
RUN python3 manage.py migrate
RUN python3 manage.py makemigrations interface
RUN python3 manage.py migrate interface
ENTRYPOINT uwsgi --ini uwsgi.ini
