# Stage 1 - Build
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY public ./public
COPY src ./src

RUN npm run build

# Stage 2 - Serve
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]