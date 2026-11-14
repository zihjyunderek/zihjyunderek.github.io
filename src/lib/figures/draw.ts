/**
 * Drawing a chart as SVG text at build time. Nothing here reaches the
 * browser as script: Observable Plot runs once, inside the build, against a
 * stand-in DOM, and the page receives the finished picture.
 *
 * Two chart types go through Plot:
 *  - `dot`   one row per `y` value, a dot at each `x` value
 *  - `cell`  a grid of `y` rows by `x` columns, one colored cell per pair
 *
 * Rows are laid out here, not by Plot (`layoutRows`), so that a group's name
 * gets a band of its own with space above it, and no line ever runs through
 * text. Plot handles the horizontal scale and writes the SVG.
 *
 * Besides the picture, each drawing lists where its values sit (in percent of
 * the picture), so the page can lay a hover label over each one with CSS alone.
 */
import * as Plot from '@observablehq/plot';
import { parseHTML } from 'linkedom';
import { classify } from './classes';
import { levels, num, type Row } from './data';
import {
  FS_DATA, FS_NAME, GROUP_GAP, HEAD, INK, INK_2, INK_3, MONO, NAME_LINE, NONE, PAPER, ROW, RULE, SERIES, SERIF,
} from './theme';

export interface LegendItem {
  token: string;
  label: string;
}

/** A value's place in the picture, in percent, and what to say about it on hover. */
export interface Hit {
  left: number;
  top: number;
  /** set for cells, whose target is the cell itself; a dot gets a fixed-size target */
  width?: number;
  height?: number;
  /** dots that touch share one target, stretched from the first dot to the last by this much */
  span?: number;
  /** what each value is, and the number; a shared target starts with the row's name, then one line per value */
  lines: { name: string; value: string }[];
}

export interface Drawing {
  svg: string;
  legend: LegendItem[];
  hits: Hit[];
}

export interface ChartSpec {
  type: 'dot' | 'cell';
  rows: Row[];
  /** the rows the color scale covers: these rows, or every view's rows */
  scaleRows: Row[];
  x: string;
  y: string;
  color?: string;
  group?: string;
  detail?: string;
  text?: string;
  order?: string[];
  /** legend label for cells whose color column is blank */
  blank: string;
  xLabel?: string;
  log?: boolean;
  reference?: number;
  referenceLabel?: string;
  /** read by screen readers in place of the picture */
  label: string;
}

/**
 * Estimated width of serif text in px, used to reserve room for row and
 * column names. The build has no browser to measure with, so each character
 * counts by its class, in em, calibrated on Source Serif 4.
 */
function textWidth(text: string, size = FS_NAME): number {
  let em = 0;
  for (const char of text) {
    if (/[A-Z]/.test(char)) em += 0.72;
    else if (char === ' ') em += 0.25;
    else if (/[a-z0-9]/.test(char)) em += 0.55;
    else em += 0.32;
  }
  return em * size;
}

const pct = (part: number, whole: number): number => Math.round((part / whole) * 10000) / 100;

/**
 * Dots on one row closer than this, in px, share one hover target. A target
 * is 12px wide (24px for a finger, so 12px either side of the dot), and a
 * picture can be shown up to about 15% smaller than it is drawn.
 */
const TOUCH = 15;

/** "A", "A and B", "A, B and C". */
const listOf = (names: string[]): string =>
  names.length < 2 ? names.join('') : `${names.slice(0, -1).join(', ')} and ${names[names.length - 1]}`;

interface RowLayout {
  /** every `y` value, the vertical center of its row and of its name, in px from the top of the picture */
  items: { name: string; y: number; nameY: number }[];
  /** every group name and the center of its band */
  headers: { name: string; y: number }[];
  /** the stretches that hold data and no text; vertical lines are drawn inside these only */
  spans: { top: number; bottom: number }[];
  /** center of the row that holds a given `y` value */
  at: (name: string) => number;
  bottom: number;
}

/**
 * The rows of a chart, top to bottom, starting at `top`: every `y` value in
 * file order. With `group`, each group opens with a band for its name and
 * every group after the first is set off by extra space. With `stacked`,
 * each row's name gets a line of its own above the row, for charts too
 * narrow to hold names beside the plot.
 */
function layoutRows(rows: Row[], y: string, group: string | undefined, top: number, stacked = false): RowLayout {
  const groups = group
    ? levels(rows, group).map((name) => ({ name, members: levels(rows.filter((row) => row[group] === name), y) }))
    : [{ name: '', members: levels(rows, y) }];
  const all = groups.flatMap((g) => g.members);
  if (new Set(all).size !== all.length) throw new Error(`a "${y}" value appears under more than one "${group}".`);

  const items: RowLayout['items'] = [];
  const headers: RowLayout['headers'] = [];
  const spans: RowLayout['spans'] = [];
  let cursor = top;
  groups.forEach(({ name, members }, index) => {
    if (group) {
      if (index > 0) cursor += GROUP_GAP;
      headers.push({ name, y: cursor + HEAD / 2 });
      cursor += HEAD;
    }
    const start = cursor;
    for (const member of members) {
      if (stacked) {
        items.push({ name: member, nameY: cursor + NAME_LINE / 2 + 2, y: cursor + NAME_LINE + ROW / 2 });
        spans.push({ top: cursor + NAME_LINE, bottom: cursor + NAME_LINE + ROW });
        cursor += NAME_LINE + ROW;
      } else {
        items.push({ name: member, nameY: cursor + ROW / 2, y: cursor + ROW / 2 });
        cursor += ROW;
      }
    }
    if (!stacked) spans.push({ top: start, bottom: cursor });
  });
  const centers = new Map(items.map((item) => [item.name, item.y]));
  return { items, headers, spans, at: (name) => centers.get(name)!, bottom: cursor };
}

/** Room the row names need beside the plot. */
const stubWidth = (names: string[]): number => Math.ceil(Math.max(...names.map((name) => textWidth(name))) + 20);

/** Row names and group names, set flush left like the stub column of a table. */
function rowNames(layout: RowLayout) {
  const place = { frameAnchor: 'left' as const, textAnchor: 'start' as const, fontSize: FS_NAME, text: (d: { name: string }) => d.name };
  return [
    Plot.text(layout.items, { ...place, y: (d: { nameY: number }) => d.nameY, fill: INK_2 }),
    Plot.text(layout.headers, { ...place, y: (d: { y: number }) => d.y, fill: INK, fontWeight: 600 }),
  ];
}

/** A tick as printed on the axis: 0.5, 2000, 0.0001. */
const tickText = (tick: number): string => String(Number(tick.toPrecision(3)));

/** True when the tick labels, set in mono, fit side by side in `room` px. */
const ticksFit = (ticks: number[], room: number): boolean =>
  ticks.reduce((sum, tick) => sum + tickText(tick).length * FS_DATA * 0.6 + 14, 0) <= room;

/**
 * Log-axis ticks covering the data: 1, 2 and 5 times each power of ten when
 * their labels fit the axis, otherwise the powers of ten alone.
 */
function logTicks(low: number, high: number, room: number): number[] {
  for (const leads of [[1, 2, 5], [1]]) {
    const ticks: number[] = [];
    for (let power = Math.floor(Math.log10(low)) - 1; power <= Math.ceil(Math.log10(high)) + 1; power++) {
      for (const lead of leads) ticks.push(Number(`${lead}e${power}`));
    }
    const from = ticks.filter((tick) => tick <= low).pop()!;
    const to = ticks.find((tick) => tick >= high)!;
    const covering = ticks.filter((tick) => tick >= from && tick <= to);
    if (leads.length === 1 || ticksFit(covering, room)) return covering;
  }
  throw new Error('unreachable');
}

/** Round ticks covering the data on a linear axis: about six, fewer when labels would touch. */
function linearTicks(low: number, high: number, room: number): number[] {
  for (const count of [5, 3, 2]) {
    const rough = (high - low || 1) / count;
    const power = 10 ** Math.floor(Math.log10(rough));
    const step = [1, 2, 5, 10].map((lead) => lead * power).find((size) => size >= rough)!;
    const ticks: number[] = [];
    for (let tick = Math.floor(low / step) * step; tick < high + step * 0.999; tick += step) ticks.push(Number(tick.toPrecision(12)));
    if (count === 2 || ticksFit(ticks, room)) return ticks;
  }
  throw new Error('unreachable');
}

function requireNumbers(rows: Row[], column: string): void {
  const bad = rows.findIndex((row) => !Number.isFinite(num(column)(row)));
  if (bad >= 0) throw new Error(`"${column}" must be a number in every row; row ${bad + 2} holds "${rows[bad][column]}".`);
}

function drawDot(spec: ChartSpec, width: number): Drawing {
  const { rows, x, y, color, group, detail, log = false, reference, referenceLabel } = spec;
  requireNumbers(rows, x);
  const series = color ? levels(rows, color) : [];
  if (series.length > SERIES.length) {
    throw new Error(`"${color}" has ${series.length} series; a dot chart tells ${SERIES.length} apart.`);
  }
  const fill = (row: Row) => SERIES[color ? series.indexOf(row[color]) : 0];
  const value = num(x);
  const values = rows.map(value);
  const low = Math.min(...values, reference ?? Infinity);
  const high = Math.max(...values, reference ?? -Infinity);
  if (log && low <= 0) throw new Error(`"${x}" holds ${low}; a log axis needs values above zero.`);

  const names = levels(rows, y);
  // one dot per row and series: there is room to print each value beside its dot
  const sparse = rows.length <= names.length * Math.max(series.length, 1);
  // two printed values on one row go on the outer sides of their dots, so they cannot overprint;
  // the plot then starts a little further right to keep the left-hand value clear of the row names
  const paired = sparse && series.length === 2;
  // names that would take more than two fifths of the chart go above their rows instead
  const stacked = stubWidth(names) > width * 0.4;
  const marginLeft = (stacked ? 20 : stubWidth(names)) + (paired ? 36 : 0);  // 20: half of the first tick label
  const right = width - (sparse ? 56 : 16);
  const leftmost = new Map<string, number>();
  for (const row of rows) leftmost.set(row[y], Math.min(leftmost.get(row[y]) ?? Infinity, value(row)));
  const onLeft = (row: Row) => paired && value(row) === leftmost.get(row[y]) && rows.some((other) => other[y] === row[y] && value(other) > value(row));
  const ticks = log ? logTicks(low, high, right - marginLeft) : linearTicks(low, high, right - marginLeft);
  const [first, last] = [ticks[0], ticks[ticks.length - 1]];
  // every tick gets a grid line; when their labels would touch, only every second or third is labelled
  const labelled = (stride: number) => ticks.filter((_, i) => (ticks.length - 1 - i) % stride === 0);
  const tickLabels = labelled([1, 2, 3].find((stride) => ticksFit(labelled(stride), right - marginLeft)) ?? 4);
  // the axis title is centered under the plot, or under the whole chart when it is wider than the plot
  const title = spec.xLabel ?? x;
  if (textWidth(title) > width) throw new Error(`the axis title "${title}" is too long for a ${width}px chart; keep it under about 40 characters.`);
  const titleX = textWidth(title) <= right - marginLeft ? (marginLeft + right) / 2 : width / 2;

  // The reference line's name sits on the first group's band, beside the
  // group's name, when the two cannot touch. Otherwise it gets a band of its own.
  let shares = false;
  if (reference !== undefined && referenceLabel && group) {
    const along = log ? Math.log(reference / first) / Math.log(last / first) : (reference - first) / (last - first);
    const labelLeft = marginLeft + along * (right - marginLeft) - textWidth(referenceLabel) / 2;
    shares = textWidth(rows[0][group]) + 16 < labelLeft;
  }
  const marginTop = referenceLabel && !shares ? 28 : 8;
  const layout = layoutRows(rows, y, group, marginTop, stacked);
  const referenceY = shares ? layout.headers[0].y : marginTop - 14;
  const height = layout.bottom + 56;
  const printed = { x: value, y: (row: Row) => layout.at(row[y]), text: x, fontFamily: MONO, fontSize: FS_DATA, fill: INK };
  /** One mark per tick and group, so vertical lines stop at every group's name. */
  const segments = (at: number[]) => layout.spans.flatMap((span) => at.map((tick) => ({ tick, ...span })));
  const segment = { x: (d: { tick: number }) => d.tick, y1: (d: { top: number }) => d.top, y2: (d: { bottom: number }) => d.bottom };

  const plot = Plot.plot({
    ...frame(spec, width, height),
    // every axis, grid line and name is one of the marks below; Plot's own are off
    x: { type: log ? 'log' : 'linear', domain: [first, last], range: [marginLeft, right], axis: null },
    y: { type: 'identity', axis: null },
    marks: [
      Plot.ruleX(segments(ticks), { ...segment, stroke: RULE }),
      Plot.ruleY(layout.items, { y: (d: { y: number }) => d.y, x1: first, x2: last, stroke: RULE }),
      Plot.text(tickLabels, {
        x: (d: number) => d, y: layout.bottom + 10, text: tickText, lineAnchor: 'top', fontFamily: MONO, fontSize: FS_DATA, fill: INK_3,
      }),
      Plot.text([title], {
        frameAnchor: 'left', dx: titleX, y: layout.bottom + 34, text: (d: string) => d,
        textAnchor: 'middle', lineAnchor: 'top', fontSize: FS_NAME, fill: INK_2,
      }),
      ...(reference === undefined ? [] : [Plot.ruleX(segments([reference]), { ...segment, stroke: INK_2, strokeWidth: 1.25 })]),
      ...(reference === undefined || !referenceLabel ? [] : [
        Plot.text([reference], { x: (d: number) => d, y: referenceY, text: () => referenceLabel, fontSize: FS_NAME, fill: INK_2 }),
      ]),
      ...rowNames(layout),
      Plot.dot(rows, { x: value, y: (row: Row) => layout.at(row[y]), fill, r: 5, stroke: PAPER, strokeWidth: 1.5 }),
      ...(sparse ? [
        Plot.text(rows.filter((row) => !onLeft(row)), { ...printed, textAnchor: 'start', dx: 10 }),
        Plot.text(rows.filter(onLeft), { ...printed, textAnchor: 'end', dx: -10 }),
      ] : []),
    ],
  });

  // Dots that touch hide one another, and so would their hover targets: they
  // share one target whose label names the row once, then lists the values
  // left to right, one line each.
  const sx = plot.scale('x')!;
  const hits: Hit[] = [];
  for (const name of names) {
    const dots = rows
      .filter((row) => row[y] === name)
      .map((row) => ({ row, at: sx.apply(value(row)) as number }))
      .sort((a, b) => a.at - b.at);
    const clusters: (typeof dots)[] = [];
    for (const dot of dots) {
      const last = clusters[clusters.length - 1];
      if (last && dot.at - last[last.length - 1].at < TOUCH) last.push(dot);
      else clusters.push([dot]);
    }
    for (const cluster of clusters) {
      const lines = new Map<string, { row: Row; details: string[] }>();
      for (const { row } of cluster) {
        const key = [row[x], color ? row[color] : ''].join('\u0000');
        const line = lines.get(key) ?? { row, details: [] };
        if (detail) line.details.push(row[detail]);
        lines.set(key, line);
      }
      const [first, last] = [cluster[0].at, cluster[cluster.length - 1].at];
      const shared = lines.size > 1;
      hits.push({
        left: pct(first, width),
        top: pct(layout.at(name), height),
        ...(last > first ? { span: pct(last - first, width) } : {}),
        lines: [
          ...(shared ? [{ name, value: '' }] : []),
          ...[...lines.values()].map(({ row, details }) => ({
            name: [shared ? '' : name, listOf(details), color && row[color]].filter(Boolean).join(', '),
            value: row[x],
          })),
        ],
      });
    }
  }
  return {
    svg: (plot as unknown as { outerHTML: string }).outerHTML,
    legend: series.map((label, i) => ({ label, token: SERIES[i] })),
    hits,
  };
}

function drawCell(spec: ChartSpec, width: number): Drawing {
  const { rows, x, y, color, group, text, order, blank } = spec;
  if (!color) throw new Error('a cell chart needs color="<column>".');
  const columns = levels(rows, x);
  const classes = classify(spec.scaleRows, color, order);

  const marginLeft = stubWidth(levels(rows, y));
  if (marginLeft > width / 2) {
    throw new Error(`the row names are too long for a ${width}px chart; keep them under about 20 characters.`);
  }
  const band = (width - marginLeft) / columns.length;
  const longest = Math.max(...columns.map((column) => textWidth(column)));
  // column names that do not fit their column are turned to read upward
  const upright = longest + 8 > band;
  const marginTop = upright ? Math.ceil(longest) + 16 : 30;
  const layout = layoutRows(rows, y, group, marginTop);
  const height = layout.bottom + 2;
  const tokens = [NONE, ...classes.list.map((c) => c.token)];

  const plot = Plot.plot({
    ...frame(spec, width, height),
    x: { type: 'band', domain: columns, range: [marginLeft, width], padding: 0, axis: null },
    y: { type: 'identity', axis: null },
    color: { type: 'ordinal', domain: tokens.map((_, i) => i - 1), range: tokens },
    marks: [
      Plot.text(columns, {
        x: (d: string) => d, y: marginTop - (upright ? 8 : 10), text: (d: string) => d, fontSize: FS_NAME, fill: INK_2,
        ...(upright ? { rotate: -90, textAnchor: 'start' as const } : { lineAnchor: 'bottom' as const }),
      }),
      ...rowNames(layout),
      // 1px inset on every side leaves a 2px paper gap between neighbours
      Plot.barY(rows, {
        x, y1: (row: Row) => layout.at(row[y]) - ROW / 2, y2: (row: Row) => layout.at(row[y]) + ROW / 2,
        fill: (row: Row) => classes.of(row), inset: 1,
      }),
      ...(text ? [
        Plot.text(rows, {
          x, y: (row: Row) => layout.at(row[y]), text, fontFamily: MONO, fontSize: FS_DATA,
          fill: (row: Row) => (classes.list[classes.of(row)]?.dark ? PAPER : INK),
        }),
      ] : []),
    ],
  });

  const sx = plot.scale('x')!;
  return {
    svg: (plot as unknown as { outerHTML: string }).outerHTML,
    legend: [
      ...classes.list.map(({ label, token }) => ({ label, token })),
      ...(classes.hasNone ? [{ label: blank, token: NONE }] : []),
    ],
    hits: rows.map((row) => ({
      left: pct(sx.apply(row[x]), width),
      top: pct(layout.at(row[y]) - ROW / 2, height),
      width: pct(sx.bandwidth!, width),
      height: pct(ROW, height),
      lines: [{ name: `${row[y]}, ${row[x]}`, value: row[color] === '' ? blank : row[color] }],
    })),
  };
}

/** Options every chart shares: the stand-in DOM, the size, and the site's type. */
function frame(spec: ChartSpec, width: number, height: number) {
  const { document } = parseHTML('<!doctype html><html><body></body></html>');
  return {
    document,
    width,
    height,
    margin: 0,
    ariaLabel: spec.label,
    style: { fontFamily: SERIF, fontSize: `${FS_NAME}px`, background: 'none', overflow: 'visible' },
  };
}

export function draw(spec: ChartSpec, width: number): Drawing {
  return spec.type === 'dot' ? drawDot(spec, width) : drawCell(spec, width);
}
