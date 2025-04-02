# # build env
# FROM node:21.7.1-alpine
# WORKDIR /app
# COPY package*.json ./
# RUN npm install
# COPY . ./
# RUN npm run build
# CMD cp -r build result_build

# Минимальный образ Nginx
FROM nginx:1.25.4-alpine

# Копируем готовую статику
COPY build/ /usr/share/nginx/html/