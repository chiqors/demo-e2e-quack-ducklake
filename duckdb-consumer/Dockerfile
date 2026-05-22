FROM node:22-slim
WORKDIR /app
COPY package.json /app/package.json
RUN npm install --omit=dev
COPY query_worker.mjs /app/query_worker.mjs
