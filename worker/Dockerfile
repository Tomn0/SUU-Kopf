FROM python:3.11

WORKDIR /app
COPY . /app

RUN pip3 install flask
RUN pip3 install APScheduler
RUN pip3 install jsonpickle

ENV FLASK_APP=worker.py

EXPOSE 80

CMD ["flask", "--app", "worker.py", "run", "--host=0.0.0.0", "--port=80", "--debug"]