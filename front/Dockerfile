FROM node:lts 
WORKDIR /app

COPY . .

RUN npm i
RUN npm install -g nodemon

ENV HOST 0.0.0.0
ENV PORT 443

EXPOSE 443
CMD npm run dev