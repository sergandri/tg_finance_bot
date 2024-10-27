FROM python:3.12-alpine
RUN apk update && apk add --no-cache gcc musl-dev libffi-dev
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app_data
EXPOSE 8200
CMD ["python", "bot.py"]
