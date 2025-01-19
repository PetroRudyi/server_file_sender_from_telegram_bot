# Використовуємо офіційний образ Python
FROM python:3.11-alpine
LABEL authors="Piter"
LABEL maintainer="Piter"
LABEL image_name="telegram-logger-truenas"

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файл програми
COPY . .

# Встановлюємо права на виконання
RUN chmod +x ./main.py


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Встановлюємо команду за замовчуванням для запуску програми
CMD ["python", "-u", "./main.py"]
