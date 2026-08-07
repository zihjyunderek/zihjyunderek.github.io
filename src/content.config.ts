import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * Projects live in `src/content/projects/*.md`.
 * Adding a project to the site = adding ONE markdown file. No code changes.
 *
 * Frontmatter contract (validated at build time — typos fail the build):
 *  - title     : project name shown everywhere
 *  - tagline   : one-line summary (also used as the page meta description)
 *  - domain    : spatial | urban | finance | engineering
 *  - stack     : tech list, rendered as chips
 *  - stats     : 2–4 headline numbers, rendered like a model card
 *  - featured  : true => pinned first on the home page (home always shows 6)
 *  - order     : sort key within the projects index (low = first)
 *  - repo      : GitHub URL (private links allowed); omit to hide the button
 *  - status    : public | private | research (controls the badge)
 */
const projects = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    tagline: z.string().max(220),
    domain: z.enum(['spatial', 'urban', 'finance', 'engineering']),
    stack: z.array(z.string()),
    stats: z
      .array(z.object({ value: z.string(), label: z.string() }))
      .min(1)
      .max(4),
    featured: z.boolean().default(false),
    order: z.number().default(99),
    repo: z.string().url().optional(),
    status: z.enum(['public', 'private', 'research']).default('public'),
  }),
});

export const collections = { projects };
