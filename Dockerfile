FROM jordanirabor/python3.7-pip-pipenv
COPY port_proxy /root/port_proxy
WORKDIR /root/port_proxy
RUN pip3 install -r requirements.md -i https://pypi.doubanio.com/simple/  --trusted-host pypi.doubanio.com
RUN python3 manage.py migrate
RUN python manage.py makemigrations interface
RUN python manage.py migrate interface
ENTRYPOINT uwsgi --ini uwsgi.ini