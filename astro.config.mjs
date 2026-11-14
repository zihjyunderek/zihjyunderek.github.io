// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// Single source of truth for the production URL.
// GitHub Pages user site => repo must be named `zihjyunderek.github.io`.
export default defineConfig({
  site: 'https://zihjyunderek.github.io',
  // Astro 7 defaults to 'jsx' whitespace rules, which drop the space between
  // inline elements (nav links, breadcrumb, footer, stat value and label).
  // `true` keeps the HTML-aware compression these templates are written for.
  compressHTML: true,
  integrations: [
    // Project pages that show figures are `.mdx`, so prose can place a
    // `<Figure />` between paragraphs. Pages without figures stay `.md`.
    mdx(),
    // `/sitemap.xml` is a hand-written mirror of the generated index, kept
    // for crawlers that only probe the conventional path. Exclude it so the
    // sitemap does not list a sitemap as a page.
    sitemap({ filter: (page) => !page.endsWith('/sitemap.xml') }),
  ],
});
