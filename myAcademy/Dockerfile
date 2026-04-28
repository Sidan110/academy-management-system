FROM python:3.11.6-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /usr/src/app/entrypoint.sh

EXPOSE 8000

CMD ["/usr/src/app/entrypoint.sh"]
