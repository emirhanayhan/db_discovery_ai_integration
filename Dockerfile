FROM python:3.13-bullseye
WORKDIR /app
ADD . /app
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
ENV PORT 8000
EXPOSE $PORT
ENV CONFIG prod
ENV MIGRATE true
CMD python /app/main.py --config=$CONFIG --migrate=$MIGRATE
