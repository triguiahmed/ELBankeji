# Stage 1: Build the Angular app
FROM node:16 as builder

WORKDIR /app

# Copy package.json and package-lock.json first to install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the Angular project

RUN npm run build -- --base-href /angular-chatbot/

# Stage 2: Serve the app with Nginx
FROM nginx:alpine

# Copy the build artifacts to the Nginx HTML directory
COPY --from=builder /app/src /usr/share/nginx/html

# Copy a default nginx config file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
