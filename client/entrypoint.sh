echo \
"export const environment = {\n\
    production: true,\n\
    API_URL: \"$API_URL\" ?? \"http://api:8000\",\n\
    API_ENDPOINT: \"$API_ENDPOINT\" ?? \"/api/\",\n\
};" > /app/src/environments/environment.ts

echo \
"export const environment = {\n\
    production: false,\n\
    API_URL: \"$API_URL\" ?? \"http://api:8000\",\n\
    API_ENDPOINT: \"$API_ENDPOINT\" ?? \"/api/\",\n\
};" > /app/src/environments/environment.development.ts

echo "{\n\
    \"$API_ENDPOINT*\": {\n\
        \"target\": \"$API_URL\",\n\
        \"secure\": false,\n\
        \"pathRewrite\": {\"^$API_ENDPOINT\" : \"/\"},\n\
        \"changeOrigin\": true,\n\
        \"logLevel\": \"debug\"\n\
    }\n\
}" > /app/src/proxy.conf.json

npm run start