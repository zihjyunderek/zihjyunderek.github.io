// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Single source of truth for the production URL.
// GitHub Pages user site => repo must be named `zihjyunderek.github.io`.
export default defineConfig({
  site: 'https://zihjyunderek.github.io',
  integrations: [
    // `/sitemap.xml` is a hand-written mirror of the generated index, kept
    // for crawlers that only probe the conventional path. Exclude it so the
    // sitemap does not list a sitemap as a page.
    sitemap({ filter: (page) => !page.endsWith('/sitemap.xml') }),
  ],
});
