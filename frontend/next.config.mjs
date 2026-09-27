import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendRoot = dirname(fileURLToPath(import.meta.url));
const maplibreDist = resolve(frontendRoot, 'node_modules/maplibre-gl/dist');
const publicDir = resolve(frontendRoot, 'public');
mkdirSync(publicDir, { recursive: true });
for (const asset of ['maplibre-gl-worker.mjs', 'maplibre-gl-shared.mjs']) {
  copyFileSync(resolve(maplibreDist, asset), resolve(publicDir, asset));
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

export default nextConfig;
