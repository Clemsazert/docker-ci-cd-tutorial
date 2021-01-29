# ---------------------- Stage 1 : Development purpose ---------------------- #

FROM node:alpine3.12 as base-app

WORKDIR /app

COPY . /app

RUN npm install

# ---------------------- Stage 2: Production environment -------------------- #

FROM node:alpine3.12
WORKDIR /app

# Dependencies
ENV NODE_ENV production
COPY package*.json ./
RUN npm install --only=prod

# Copy files
COPY --from=base-app /app ./

# Launch
CMD ["node", "index.js"]