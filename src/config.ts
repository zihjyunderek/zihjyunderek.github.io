/**
 * Site-wide configuration, the only file to touch when identity,
 * links, or wording change. Every SEO input (title, description,
 * keywords, names) lives here; layouts and JSON-LD read from it.
 */
export const SITE = {
  url: 'https://zihjyunderek.github.io',
  name: 'Zih-Jyun Huang (Derek)',
  /** Legal Chinese name. Rendered in the hero, footer, title, and JSON-LD. */
  alternateName: '黃子竣',
  shortName: 'Derek Huang',
  jobTitle: 'Data Analyst',
  /** Current employer. Leave '' between roles; JSON-LD then omits worksFor. */
  org: '',
  title: 'Zih-Jyun (Derek) Huang 黃子竣',
  description:
    'Portfolio of Zih-Jyun (Derek) Huang (黃子竣): spatial statistics, urban analytics, quantitative risk. Formerly Gensler Research Institute, incoming risk management MA at CTBC Bank.',
  email: 'derek4953098@gmail.com',
  github: 'https://github.com/zihjyunderek',
  linkedin: 'https://www.linkedin.com/in/derekhuang0426/',
  locations: {
    base: { city: 'Xinyi, Taipei', code: 'TPE', coords: '25.03°N 121.57°E' },
  },
  /**
   * SEO keywords, ordered name → method → affiliation.
   * Bilingual on purpose: the Chinese legal name is the highest-value
   * query. Add new terms here only; nothing else needs to change.
   */
  keywords: [
    'Zih-Jyun Huang',
    'Derek Huang',
    '黃子竣',
    'Huang Zih-Jyun',
    'spatial statistics',
    'MGWR',
    'geographically weighted regression',
    'urban analytics',
    'Value at Risk',
    'implied volatility',
    'quantitative finance',
    'risk management',
    'Python',
    'data science portfolio',
    'Gensler Research Institute',
    'CTBC Bank',
    'National Chengchi University',
    'National Taiwan University',
    '空間統計',
    '風險管理',
    '資料科學',
  ],
} as const;

/** Display labels for the four project domains. */
export const DOMAINS: Record<string, string> = {
  spatial: 'Geospatial Statistics',
  urban: 'Urban Analytics',
  finance: 'Quantitative Finance',
  engineering: 'Engineering and Agentic Systems',
};
