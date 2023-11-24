FROM python:3.8.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./app/lib/requirements.txt /code/app/lib/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/app/lib/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--reload",  "--host", "0.0.0.0", "--port", "3000"]