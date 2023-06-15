FROM python:3.11
ADD . .

RUN pip install flask
RUN pip install requests

CMD python ./master.py --verbose