FROM node:20 AS fe
WORKDIR /fe
COPY frontend/package.json ./
RUN npm install
COPY frontend .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend .
COPY --from=fe /fe/dist ./frontend_dist
ENV DEBUG=0 PORT=8000
CMD gunicorn config.wsgi --bind 0.0.0.0:$PORT --timeout 120 --workers 2
