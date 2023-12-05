FROM public.ecr.aws/docker/library/python:3.9.4

# RUN pip install pipenv

WORKDIR /app

COPY . /app

# RUN pipenv sync --system
