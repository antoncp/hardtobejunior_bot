FROM python:3.9-slim
WORKDIR /hardtobejunior_bot
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ["python", "main.py"]