FROM python:3.11-slim

WORKDIR /app

COPY rtun ./rtun

EXPOSE 3001/tcp

RUN useradd -m -u 10001 ctfuser
USER ctfuser

CMD ["python3", "-m", "rtun.server"]
