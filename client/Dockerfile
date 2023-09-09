FROM node:18.10

COPY ssl /ssl

WORKDIR /app
COPY client/package*.json .
RUN npm install
COPY client .
COPY client/entrypoint.sh /tmp/

CMD [ "sh", "-x", "/tmp/entrypoint.sh" ]