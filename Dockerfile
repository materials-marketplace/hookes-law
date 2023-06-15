FROM python:3.9

WORKDIR /app
ADD . .
RUN python3 -m pip install .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# docker compose up
