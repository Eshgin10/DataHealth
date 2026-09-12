FROM node:22-bookworm-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1
ENV API_URL=http://127.0.0.1:8000
RUN npm run build

FROM python:3.13-slim-bookworm
COPY --from=frontend-build /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ ./backend/
COPY sample-data/ ./sample-data/
COPY deploy/start.py ./deploy/start.py
COPY --from=frontend-build /app/frontend/.next/standalone ./frontend/
COPY --from=frontend-build /app/frontend/.next/static ./frontend/.next/static/
COPY --from=frontend-build /app/frontend/public ./frontend/public/
ENV PYTHONPATH=/app PYTHONUNBUFFERED=1 NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000 HOSTNAME=0.0.0.0
EXPOSE 3000
CMD ["python", "/app/deploy/start.py"]
