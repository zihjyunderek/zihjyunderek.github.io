// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Single source of truth for the production URL.
// GitHub Pages user site => repo must be named `zihjyunderek.github.io`.
export default defineConfig({
  site: 'https://zihjyunderek.github.io',
  integrations: [sitemap()],
});
