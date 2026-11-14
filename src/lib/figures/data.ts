/**
 * Reading the CSV behind a figure.
 *
 * Input rule: what the CSV says is what the figure prints. Cells stay
 * strings; a column is read as a number only where a mark needs a position
 * or a color class, so `0.130` in the file is printed as 0.130.
 *
 * Every error thrown under `src/lib/figures/` is a plain sentence about the
 * input; Figure.astro puts the project and file name in front of it.
 */
import fs from 'node:fs';
import path from 'node:path';
import { csvParse } from 'd3-dsv';

export type Row = Record<string, string>;

/** Load `src/data/figures/<slug>/<file>` and check every column the figure names. */
export function loadRows(slug: string, file: string, columns: (string | undefined)[]): Row[] {
  const relative = `src/data/figures/${slug}/${file}`;
  const absolute = path.join(process.cwd(), relative);
  if (!fs.existsSync(absolute)) throw new Error(`${relative} does not exist.`);
  const table = csvParse(fs.readFileSync(absolute, 'utf-8').replace(/^﻿/, ''));
  if (table.length === 0) throw new Error(`${relative} has no rows.`);
  for (const column of columns) {
    if (column && !table.columns.includes(column)) {
      throw new Error(`there is no column "${column}" (the file has: ${table.columns.join(', ')}).`);
    }
  }
  return [...table];
}

/** Distinct values of a column, in the order they first appear in the file. */
export const levels = (rows: Row[], column: string): string[] => [...new Set(rows.map((row) => row[column]))];

/** True when every filled cell of a column is a number as printed: 1,470 or −0.32 or 12.5%. */
export const isNumeric = (rows: Row[], column: string): boolean =>
  rows.some((row) => row[column] !== '') && rows.every((row) => row[column] === '' || /^[−-]?[\d,]*\.?\d+%?$/.test(row[column]));

/**
 * Read a column as a number. A blank cell is NaN, which marks "no value".
 * A typographic minus and thousands separators are read as printed: −0.3, 1,470.
 */
export const num = (column: string) => (row: Row): number =>
  row[column] === '' ? NaN : Number(row[column].replace(/−/g, '-').replace(/,/g, ''));
