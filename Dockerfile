 FROM python:3.8-slim-buster

WORKDIR /app

EXPOSE 5000

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

CMD [ "python", "api.py" ]
