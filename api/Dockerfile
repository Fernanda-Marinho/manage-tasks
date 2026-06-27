FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# migration
CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0"] 

# without migration
#CMD ["flask", "run", "--host=0.0.0.0"] 

EXPOSE 5000