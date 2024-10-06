FROM node:18-alpine

WORKDIR /frontend

COPY package.json package-lock.json ./

RUN npm install

COPY . .

EXPOSE 3000

#CMD ["node", "frontend.js"]
CMD ["npm", "start"]