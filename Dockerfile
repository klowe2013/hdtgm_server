FROM python:3.9-slim

WORKDIR /hdtgm-player/

COPY . .
RUN pip3 install -r requirements.txt

# ENTRYPOINT ["python", "app.py"]
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]