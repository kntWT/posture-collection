FROM node:18.10

COPY ssl /ssl

WORKDIR /app
COPY client/package*.json .
RUN npm install
COPY client .
# COPY client/entrypoint.sh /tmp/

RUN { \
    echo "export const environment = {\n";\
    echo "\tproduction: false,\n";\
    echo "\tAPI_URL: \"$API_URL\" ?? \"http://api:8000\",\n";\
    echo "\tAPI_ENDPOINT: \"$API_ENDPOINT\" ?? \"/api/\",\n";\
    echo "};";\
} > /app/src/environments/environment.ts

RUN { \
    echo "export const environment = {\n";\
    echo "\tproduction: true,\n";\
    echo "\tAPI_URL: \"$API_URL\" ?? \"http://api:8000\",\n";\
    echo "\tAPI_ENDPOINT: \"$API_ENDPOINT\" ?? \"/api/\",\n";\
    echo "};";\
} > /app/src/environments/environment.development.ts

RUN { \
    echo "{\n";\
    echo "\t\"$API_ENDPOINT*\": {\n";\
    echo "\t\t\"target\": \"$API_URL\",\n";\
    echo "\t\t\"secure\": false,\n";\
    echo "\t\t\"pathRewrite\": {\"^$API_ENDPOINT\" : \"/\"},\n";\
    echo "\t\t\"changeOrigin\": true,\n";\
    echo "\t\t\"logLevel\": \"debug\"\n";\
    echo "\t}\n";\
    echo "}"; \
} > /app/src/environments/environment.ts

# CMD [ "sh", "-c", "/tmp/entrypoint.sh" ]
CMD ["npm", "run", "start"]