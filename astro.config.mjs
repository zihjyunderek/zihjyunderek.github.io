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
  // Project pages merged or renamed in the November 2026 reorganization keep
  // their old addresses alive for links and search engines already indexed.
  redirects: {
    '/projects/decoding-the-city-mgwr': '/projects/multiscale-gwr/',
    '/projects/mgwr-toolkit': '/projects/multiscale-gwr/',
    '/projects/archetype-clustering': '/projects/city-clusters/',
    '/projects/kmedoids-archetype': '/projects/city-clusters/',
    '/projects/urban-exclusion-index': '/projects/city-indices/',
    '/projects/composite-index-suite': '/projects/city-indices/',
    '/projects/survey-composite-score': '/projects/city-survey/',
    '/projects/pygrf-spatial-ml': '/projects/gw-rf/',
    '/projects/gwpca-r-wrapper': '/projects/gw-pca/',
    '/projects/pygwpcc': '/projects/gw-corr/',
    '/projects/spatial-factor-analysis': '/projects/spatial-fa/',
    '/projects/python-notebook-toolkit': '/projects/',
  },
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
