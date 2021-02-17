FROM node:12

WORKDIR /app

RUN npm install -g nodemon

COPY package*.json ./

RUN npm install

COPY . .

ENV PORT 2411

EXPOSE 2411

CMD ["node", "index.js"]