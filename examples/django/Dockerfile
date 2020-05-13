FROM python:3
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

ADD ./python-sdk/ ./python-sdk/
RUN pip install ./python-sdk/

COPY . /app/

RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver",  "0.0.0.0:8000"]
