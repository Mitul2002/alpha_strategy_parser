# Multi-stage build: compile the Vue/Vite app, then serve the static output
# with nginx. Backend API base URL is hardcoded to http://127.0.0.1:8000 in
# backendService.js -- that's fine here because the browser (not the
# container) makes that call, and docker-compose publishes the backend on
# the host's localhost:8000, so it resolves correctly with no rebuild-time
# env injection needed.
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
