FROM python:3-buster
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY main.py .
RUN ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime
CMD ["python", "./main.py"]