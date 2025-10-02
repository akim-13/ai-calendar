FROM node:20-alpine

WORKDIR /app

# Install deps using the lockfile.
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy the rest of the source code.
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

