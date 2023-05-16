FROM python:3.11
ADD . /src

RUN pip install kopf
RUN pip install requests
RUN pip install kubernetes
# other pip installs can be done here

CMD kopf run /src/rsacracker.py --verbose