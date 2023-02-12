FROM python:3

WORKDIR /app

RUN apt-get update && apt-get install -y locales && locale-gen id_ID.UTF-8

COPY requirements.txt ./

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install -r requirements.txt

COPY . .

ENV PORT=8080

EXPOSE 8080

CMD ["python", "bot.py"]