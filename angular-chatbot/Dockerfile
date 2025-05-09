FROM node:14

WORKDIR /app


# Copy Angular project files
COPY package*.json angular.json tsconfig.json ./
COPY src ./src
COPY e2e ./e2e 
COPY . .

RUN npm install

EXPOSE 4200

CMD ["ng", "serve", "--host", "0.0.0.0", "--poll=2000"]
