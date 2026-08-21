import type { APIRoute } from 'astro';
import { SITE } from '../config';

/**
 * `/sitemap.xml` — conventional alias for the generated sitemap index.
 *
 * `@astrojs/sitemap` writes `/sitemap-index.xml` and `/sitemap-0.xml`, and
 * `robots.txt` points at the index. Several crawlers and validators never
 * read robots.txt and probe `/sitemap.xml` directly, which returned 404.
 * This mirrors the index so both paths resolve to the same URL list.
 *
 * Astro emits this as a static file at build time; GitHub Pages serves it
 * as `application/xml` from the extension. `astro.config.mjs` filters this
 * route out of the generated sitemap so it is not listed as a page.
 */
export const GET: APIRoute = () => {
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>${SITE.url}/sitemap-0.xml</loc>
  </sitemap>
</sitemapindex>
`;

  return new Response(body, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};
