FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libcairo2

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/bin/bash"]