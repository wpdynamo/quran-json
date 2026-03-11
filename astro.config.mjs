import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://quran-json-sigma.vercel.app',
  output: 'static',
  build: {
    format: 'directory'
  },
  outDir: './dist',
  integrations: [sitemap()]
});
