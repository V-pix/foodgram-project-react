FROM python:3.8-slim

WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

# RUN pip3 install --upgrade pip

RUN pip3 install --upgrade pip

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY foodgram/ /app

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"] 

# CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]