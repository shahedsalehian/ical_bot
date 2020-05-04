FROM python:3
WORKDIR /app
RUN pip3 install discord.py
RUN pip3 install ics
COPY . .
CMD ["python", "./main.py"]


