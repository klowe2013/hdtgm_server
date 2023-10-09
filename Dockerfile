# FROM python:3.8-slim-buster
FROM python:3.8-buster

WORKDIR /hdtgm-player/

COPY . .
# apt-get install libxml2-dev libxslt-dev python-dev \

RUN pip3 install --upgrade pip  \ 
    && pip3 install -r requirements.txt \
    && mkdir -p ./media/audio_files

# ENTRYPOINT ["python", "main.py", "--host=0.0.0.0"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
