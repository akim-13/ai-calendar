FROM node:20-alpine

WORKDIR /app

# Install deps using the lockfile.
COPY package*.json ./
# NOTE: If executables inside the container are missing/corrupted,
# delete node_modules and run `npm ci` manually inside it.
RUN npm ci

# Copy the rest of the source code.
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
#CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
