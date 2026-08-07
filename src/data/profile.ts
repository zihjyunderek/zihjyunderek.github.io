/**
 * Profile data: experience, education, skills, certificates.
 * Update THIS file when your CV changes; pages render from it automatically.
 * The one-page CV is generated from `scripts/build_cv.py`, which mirrors
 * this file; change both together.
 *
 * Attachments are publishable evidence only: the thesis (already public via
 * the university), the competition award, and certificate licenses. Diplomas
 * and employer deliverables are excluded on purpose (identity documents,
 * NDA), so those entries carry no attachment field at all. Never add one
 * back for a document that cannot be public.
 * Files live in `public/attachments/{experience|education|certificates}/`.
 */

export interface Attachment {
  label: string;
  href: string;
}

export interface ExperienceEntry {
  org: string;
  role: string;
  when: string;
  where: string;
  note: string;
  /** Publishable evidence only; omit when nothing may be published. */
  attachments?: Attachment[];
}

export interface EducationEntry {
  school: string;
  degree: string;
  when: string;
  detail: string;
  /** Thesis title; rendered on the skills page when present. */
  thesis?: string;
  /** Publishable evidence only; omit when nothing may be published. */
  attachments?: Attachment[];
}

export interface Certificate {
  name: string;
  attachments: Attachment[];
}

export const experience: ExperienceEntry[] = [
  {
    org: 'CTBC Bank',
    role: 'Incoming Management Associate, Risk Management',
    when: '2027/02 (expected)',
    where: 'Taipei',
    note: 'Admitted to the CTBC Management Associate program, risk management track. Onboarding is expected in February 2027, after completion of military service.',
  },
  {
    org: 'Republic of China Army',
    role: 'Compulsory Military Service',
    when: '2026/08 – 2026/12',
    where: 'Taiwan',
    note: 'Statutory conscription of the Republic of China (Taiwan). Email remains the best way to reach me during service.',
  },
  {
    org: 'Gensler Research Institute',
    role: 'Data Analyst, Cities Research',
    when: '2025/02 – 2026/08',
    where: 'New York (remote from Taipei)',
    note: 'Statistical research on major US cities. Geospatial regression models linking urban indicators to population, home prices, and rents. Flagship study: "Decoding the City: Unveiling NYC\'s Geographical Phenomena with MGWR".',
  },
  {
    org: 'CTBC Bank',
    role: 'Intern, Market Risk Management (MRMD)',
    when: '2025/10 – 2026/02',
    where: 'Taipei',
    note: 'Returning internship with the market-risk division, focused on stablecoin risk management.',
  },
  {
    org: 'Hon Hai Precision (Foxconn)',
    role: 'Summer Intern, Risk Management',
    when: '2025/08 – 2025/09',
    where: 'New Taipei',
    note: 'FX forecasting around key macro events with the treasury "5+1" framework; reconciled trade records and analyzed internal ledgers for AR/AP position management.',
  },
  {
    org: 'CTBC Bank',
    role: 'Summer Intern, Market Risk Management (MRMD)',
    when: '2025/07 – 2025/08',
    where: 'Taipei',
    note: 'Applied machine learning and deep learning to market-risk analytics. Training across treasury structure, cross-border liquidity, and derivatives; supported FX forecasting and back-office reconciliation workflows.',
  },
  {
    org: 'Chung-hua Institution for Economic Research (CIER)',
    role: 'Project Assistant, First Division',
    when: '2023/06 – 2023/12',
    where: 'Taipei',
    note: 'Analyzed China\'s macroeconomy, wrote for the Trade Insight bi-weekly (International Trade Administration), and built an internal economic database.',
  },
  {
    org: 'CFA Research Challenge, Taiwan Final',
    role: '2nd Place, Best Written Report',
    when: '2022/09 – 2023/05',
    where: 'Taipei',
    note: 'Awarded Best Written Report for macroeconomic analysis and data visualization, grounded in on-site visits and investor conferences.',
    attachments: [
      { label: 'Report (PDF)', href: '/attachments/experience/cfa-research-challenge.pdf' },
    ],
  },
];

export const education: EducationEntry[] = [
  {
    school: 'National Chengchi University',
    degree: 'M.S. Money and Banking',
    when: '2024 – 2026',
    detail: 'GPA 4.21 / 4.3',
    thesis:
      'Forecasting FX Spot Value-at-Risk (VaR) Using Implied Volatility: Evidence from G7 Currency Pairs',
    attachments: [
      { label: 'Thesis (PDF)', href: '/attachments/education/nccu-thesis.pdf' },
    ],
  },
  {
    school: 'National Taiwan University',
    degree: 'B.A. Economics',
    when: '2020 – 2024',
    detail: 'GPA 3.6 / 4.3',
  },
];

export const certificates: Certificate[] = [
  {
    name: 'Futures Specialist',
    attachments: [
      { label: 'License (PDF)', href: '/attachments/certificates/futures-specialist.pdf' },
    ],
  },
  {
    name: 'Securities Investment Trust and Consulting Professional',
    attachments: [
      { label: 'License (PDF)', href: '/attachments/certificates/investment-trust-consulting.pdf' },
    ],
  },
  {
    name: 'Senior Securities Specialist',
    attachments: [
      { label: 'License (PDF)', href: '/attachments/certificates/senior-securities-specialist.pdf' },
    ],
  },
];

/**
 * Rendered as a "feature importance" chart:
 * what best predicts my output, normalized to [0, 1].
 */
export const featureImportance = [
  { name: 'Python', value: 0.95 },
  { name: 'Spatial statistics', value: 0.9 },
  { name: 'ML and clustering', value: 0.85 },
  { name: 'Data visualization', value: 0.8 },
  { name: 'Agentic workflows', value: 0.75 },
  { name: 'Project management', value: 0.7 },
  { name: 'R, Stata, EViews', value: 0.65 },
  { name: 'Power BI, LaTeX', value: 0.6 },
];

/** Headline numbers under the hero. */
export const headlineStats = [
  { value: '16+', label: 'repositories' },
  { value: '31', label: 'US cities modeled' },
  { value: '137', label: 'urban metrics' },
  { value: '7', label: 'clustering algorithms' },
  { value: 'G7', label: 'FX pairs (VaR)' },
];
