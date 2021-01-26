FROM python:3.7-alpine3.12

WORKDIR /app

COPY . /app

RUN pip install -r requirement.txt

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]