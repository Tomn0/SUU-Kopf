FROM python:3.11
ADD . /src

RUN pip install kopf
# other pip installs can be done here

CMD kopf run /src/rsacracker.py --verbose