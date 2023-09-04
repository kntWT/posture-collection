FROM node:18.10

COPY ssl /ssl

WORKDIR /app
COPY client/package*.json .
RUN npm install
COPY client .
# RUN npm run build

CMD ["npm", "run", "start"]