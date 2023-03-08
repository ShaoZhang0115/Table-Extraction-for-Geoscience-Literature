FROM node:16-buster as COMPILER


WORKDIR /app

COPY package.json /app

RUN npm install --force --registry=https://registry.npm.taobao.org

COPY . /app

RUN set -ex ;\
    npm run build

# ---------------------------------------------------------------------------------------

FROM node:16-buster


WORKDIR /app

COPY --from=COMPILER /app ./

LABEL project="frontend"

CMD ['npm', 'run', 'serve']