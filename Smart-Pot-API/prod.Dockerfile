FROM public.ecr.aws/lambda/python:3.9

# Set environment variables for Python to optimize for production
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /smart_pot_api

# Copy the requirements file separately and install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the content of local "app" directory to the folder "app" under the working directory "smart_pot_api"
COPY ./app ./app

# Copy the content of local ".env.production" file to the working directory "smart_pot_api"
COPY .env.production ./.env.production

CMD ["app.main.handler"]