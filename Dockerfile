# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# Set the working directory in the container to /app
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Update and upgrade apt
RUN apt-get update && apt-get upgrade -y

#Download ffmpeg
RUN apt-get install -y ffmpeg

# Add the current directory contents into the container at /app
ADD poetry.lock /app/.
ADD pyproject.toml /app/.

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --only main

ADD src /app/.
# Make port 80 available to the world outside this container
EXPOSE 80



# Run app.py when the container launches
#CMD ["tail","-f", "/dev/null"]

#CMD ["poetry","run", "python", "app.py"]
CMD ["poetry", "run", "gunicorn", "-b", "0.0.0.0:80", "youtube_web_downloader.app.app:app"]
