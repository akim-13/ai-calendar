FROM node:20-alpine

WORKDIR /app

# Install deps using the lockfile.
COPY package*.json ./
RUN npm install

# Copy the rest of the source code.
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
#CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
