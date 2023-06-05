FROM python:3.11
ADD . .

RUN pip install kopf
RUN pip install requests
RUN pip install kubernetes
RUN pip install jsonpickle
RUN pip install flask
RUN pip3 install APScheduler
# other pip installs can be done here

CMD kopf run ./rsacracker.py --verbose