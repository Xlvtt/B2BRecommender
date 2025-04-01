# Stage 1 - Build
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2 - Serve
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

#main.867b3754.js              main.867b3754.js.LICENSE.txt  main.867b3754.js.map
#main.265be170.css      main.265be170.css.map
#Убедитесь, что React-приложение монтируется в элемент с id="root".

