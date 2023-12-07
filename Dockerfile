FROM public.ecr.aws/docker/library/python:3.9.4

WORKDIR /app

# Copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY . /app
