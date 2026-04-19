# Frontend Dockerfile (Vite + React)
FROM node:20-slim

WORKDIR /app

# Do NOT copy package-lock.json — Windows lockfiles pin Windows-native rollup
# binaries which cause MODULE_NOT_FOUND on Linux.
# A fresh install resolves the correct @rollup/rollup-linux-x64-gnu binary.
COPY package.json ./

RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host"]
