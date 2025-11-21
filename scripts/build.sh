#!/usr/bin/env bash

echo "node: $(node -v)"
echo "npm: $(npm -v)"

npm install

NODE_ENV=production npm run build
