FROM python:3.12-alpine

WORKDIR /app

COPY . /app
#RUN apt-get update && apt-get install -y curl
RUN pip install --no-cache-dir -r requirements.txt 

COPY .env .env
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]