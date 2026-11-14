/**
 * The CSS tokens a figure may use. Only the names live here; the values are
 * defined once, in `src/styles/global.css`, so a figure can never drift from
 * the site's palette and no color is hard-coded in a component.
 */

/** Categorical: the accent for the subject, a neutral for what it is compared with. */
export const SERIES = ['var(--data-1)', 'var(--data-2)'];

/** Magnitude: one hue, light to dark. */
export const SEQUENTIAL = ['var(--seq-1)', 'var(--seq-2)', 'var(--seq-3)', 'var(--seq-4)', 'var(--seq-5)'];

/** Sign: strongest first below zero, strongest last above it. */
export const NEGATIVE = ['var(--neg-3)', 'var(--neg-2)', 'var(--neg-1)'];
export const POSITIVE = ['var(--pos-1)', 'var(--pos-2)', 'var(--pos-3)'];

/** Kind: categories with no order. `dark` marks fills that need light text. */
export const NOMINAL = [
  { token: 'var(--cat-1)', dark: true },
  { token: 'var(--cat-2)', dark: false },
  { token: 'var(--cat-3)', dark: false },
  { token: 'var(--cat-4)', dark: false },
  { token: 'var(--cat-5)', dark: true },
];

/** A mark with no value to show (blank cell in the CSV). */
export const NONE = 'var(--data-none)';
/** A map shape with no row in the CSV: a place outside the analysis. */
export const OUTSIDE = 'var(--data-out)';

export const INK = 'var(--ink)';
export const INK_2 = 'var(--ink-2)';
export const INK_3 = 'var(--ink-3)';
export const RULE = 'var(--rule)';
export const PAPER = 'var(--bg)';
export const SERIF = 'var(--serif)';
export const MONO = 'var(--mono)';

/**
 * Each chart is drawn once per width and CSS shows the one nearest the
 * column (`@container` rules in global.css), so text inside a chart stays
 * close to its set size on every screen instead of shrinking with the picture.
 * `wide` is the reading column at full width, `narrow` a phone.
 */
export const WIDTHS = { wide: 712, mid: 520, narrow: 350 } as const;
export type Width = keyof typeof WIDTHS;

/** Type sizes inside a chart, in px: names (= --fs-meta), then data (= --fs-data). */
export const FS_NAME = 14;
export const FS_DATA = 13;

/**
 * Vertical rhythm of a chart, in px: the height of one data row, of the band
 * that holds a group's name, and the extra space above every group but the first.
 */
export const ROW = 28;
export const HEAD = 30;
export const GROUP_GAP = 16;
/** Height of the line a row's name takes when it is set above its row instead of beside it. */
export const NAME_LINE = 20;
