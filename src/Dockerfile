FROM python:3

WORKDIR /wx-chatbot
ENV PATH="${PATH}:/usr/local/bin:/usr/bin:/bin"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install chromium xvfb xauth -y

COPY . .

CMD [ "python", "main.py" ]