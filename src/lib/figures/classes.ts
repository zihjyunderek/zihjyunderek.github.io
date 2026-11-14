/**
 * Turning a column into color classes. One function serves the marks and the
 * legend, so the two cannot disagree.
 *
 *  - text column with `order` -> ranked categories, light to dark in that order
 *  - text column without it   -> unranked categories, one distinct color each, in alphabetical order
 *  - numbers, none below 0    -> five equal steps from the smallest to the largest value
 *  - numbers, some below 0    -> three equal steps each side of zero; the sign picks the hue
 *
 * A blank cell belongs to no class and is drawn in the neutral "none" color.
 *
 * `rows` is everything the scale has to cover. For a figure with several
 * views that is usually all of them, so a color means the same thing in
 * every view; the returned `of` then classifies any row.
 */
import { levels, num, type Row } from './data';
import { NEGATIVE, NOMINAL, POSITIVE, SEQUENTIAL } from './theme';

export interface ColorClass {
  label: string;
  token: string;
  /** true when the fill is dark enough that text on it must be light */
  dark: boolean;
}

export interface Classes {
  list: ColorClass[];
  /** index into `list`, or -1 for a blank cell */
  of: (row: Row) => number;
  /** true when some rows are blank and the legend needs a "none" entry */
  hasNone: boolean;
}

/** SEQUENTIAL[3] and [4] need light text. */
const DARK_FROM = 3;

/** Spread n categories across the sequential ramp, always ending on the darkest. */
function spread(n: number): number[] {
  if (n === 1) return [SEQUENTIAL.length - 1];
  return Array.from({ length: n }, (_, i) => Math.round((i * (SEQUENTIAL.length - 1)) / (n - 1)));
}

/** Decimals that tell neighbouring class limits apart. */
function decimalsFor(step: number): number {
  if (step >= 10) return 0;
  if (step >= 1) return 1;
  return step >= 0.1 ? 2 : 3;
}

export function classify(rows: Row[], column: string, order?: string[]): Classes {
  const filled = rows.filter((row) => row[column] !== '');
  const hasNone = filled.length < rows.length;
  const value = num(column);
  const numeric = filled.length > 0 && filled.every((row) => Number.isFinite(value(row)));

  if (!numeric) {
    // unranked names are sorted so that "Archetype 2" keeps its color whatever the row order
    const names = order ?? levels(filled, column).sort((a, b) => a.localeCompare(b, 'en', { numeric: true }));
    const limit = order ? SEQUENTIAL.length : NOMINAL.length;
    if (names.length > limit) {
      throw new Error(`"${column}" has ${names.length} categories; a color scale tells ${limit} apart.`);
    }
    const unknown = levels(filled, column).find((name) => !names.includes(name));
    if (unknown !== undefined) throw new Error(`"${column}" holds "${unknown}", which is not in order="${names.join(',')}".`);
    const steps = spread(names.length);
    const paint = (i: number) => (order ? { token: SEQUENTIAL[steps[i]], dark: steps[i] >= DARK_FROM } : NOMINAL[i]);
    return {
      list: names.map((label, i) => ({ label, ...paint(i) })),
      of: (row) => names.indexOf(row[column]),
      hasNone,
    };
  }

  const values = filled.map(value);
  const low = Math.min(...values);
  const high = Math.max(...values);

  if (low < 0) {
    // one step size for both sides, so equal shades mean equal distance from zero
    const step = Math.max(-low, high) / 3;
    const d = decimalsFor(step);
    const edge = (k: number) => (k * step).toFixed(d);
    const negative = NEGATIVE.map((token, i) => ({
      label: `−${edge(3 - i)} to ${i === 2 ? '0' : `−${edge(2 - i)}`}`,
      token,
      dark: i === 0,
    }));
    const positive = POSITIVE.map((token, i) => ({
      label: `${i === 0 ? '0' : edge(i)} to ${edge(i + 1)}`,
      token,
      dark: i === 2,
    }));
    return {
      list: high > 0 ? [...negative, ...positive] : negative,
      of: (row) => {
        const v = value(row);
        if (!Number.isFinite(v)) return -1;
        const k = Math.min(2, Math.floor(Math.abs(v) / step));
        // a zero among values that are otherwise all negative joins the class nearest zero
        return v < 0 || high <= 0 ? 2 - k : 3 + k;
      },
      hasNone,
    };
  }

  const n = SEQUENTIAL.length;
  const step = (high - low) / n || 1;
  const d = decimalsFor(step);
  return {
    list: SEQUENTIAL.map((token, i) => ({
      label: `${(low + i * step).toFixed(d)} to ${(low + (i + 1) * step).toFixed(d)}`,
      token,
      dark: i >= DARK_FROM,
    })),
    of: (row) => {
      const v = value(row);
      return Number.isFinite(v) ? Math.min(n - 1, Math.floor((v - low) / step)) : -1;
    },
    hasNone,
  };
}
