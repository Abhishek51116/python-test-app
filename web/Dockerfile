FROM python:3
WORKDIR /usr/src/app
RUN adduser nir
COPY requriments.txt .
RUN pip install --no-cache-dir -r requriments.txt
COPY . .
CMD ["python","app.py"]
