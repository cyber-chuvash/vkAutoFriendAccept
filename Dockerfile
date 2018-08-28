FROM python:3.6-alpine
COPY Pipfile.lock /Pipfile.lock
COPY Pipfile /Pipfile
RUN pip install pipenv
RUN pipenv install --system
COPY main.py /app/
WORKDIR /app
CMD ["python3", "main.py"]