FROM python:3.8-slim 

WORKDIR /app
RUN mkdir -p /backup

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]