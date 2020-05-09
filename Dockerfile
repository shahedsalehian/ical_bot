FROM python:3
WORKDIR /app
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python", "./main.py"]


