import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import alpine from '@astrojs/alpinejs';

export default defineConfig({
  site: 'https://quran-json-sigma.vercel.app',
  output: 'static',
  build: {
    format: 'directory'
  },
  outDir: './dist',
  integrations: [
    alpine(),
    sitemap()
  ]
});