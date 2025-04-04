FROM python:3.12-slim-bullseye

# configuration
ENV WorkingDirectory=/usr/src/backend \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# directory containing our code inside the container
WORKDIR $WorkingDirectory

# copy whole project to your docker home directory.
COPY . $WorkingDirectory

# run this command to install all dependencies
RUN apt update
RUN apt install -y postgresql-client curl

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Startup command for running container
RUN chmod +x "$WorkingDirectory/scripts/entrypoint.sh"
CMD bash -c "$WorkingDirectory/scripts/entrypoint.sh"
