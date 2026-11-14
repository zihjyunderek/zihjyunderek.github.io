/**
 * Drawing a choropleth as SVG text at build time: every place is a shape from
 * a geometry file (`src/data/figures/geometry/<name>.json`, written by
 * scripts/figures/s06_geometry.py), filled by its class.
 *
 * A map is drawn once for all its views. Each shape carries one short class
 * per view (view 1: a0, a1 …; view 2: b0 …), and a <style> inside the SVG
 * fills them: view 1's colors by default, another view's while its switch is
 * checked (the same `:has()` test that shows that view's legend). Shapes that
 * share every class are joined into one path, so the markup stays close to
 * the size of the geometry, however many views there are. Text (the legend)
 * stays in HTML, so one drawing serves every screen width.
 */
import fs from 'node:fs';
import path from 'node:path';
import { classify } from './classes';
import type { Row } from './data';
import type { LegendItem } from './draw';
import { NONE, OUTSIDE } from './theme';

/** Shapes in drawing units: a whole-number SVG path per place. */
interface Geometry {
  source: string;
  width: number;
  height: number;
  places: Record<string, string>;
}

export interface MapView {
  rows: Row[];
  /** the rows the color scale covers: this view's rows, or every view's rows */
  scaleRows: Row[];
}

export interface MapSpec {
  views: MapView[];
  /** geometry file name, without `.json` */
  geometry: string;
  /** the column that names each row's place, as the geometry file does */
  place: string;
  color: string;
  order?: string[];
  /** legend label for rows whose color column is blank */
  blank: string;
  /** legend label for shapes with no row in a view */
  outside: string;
  /** the figure's id: the fill rules apply inside it only */
  scope: string;
  /** read by screen readers in place of the picture */
  label: string;
}

/** One letter per view in the class names; Figure.astro allows six views. */
const VIEW = 'abcdef';

const loaded = new Map<string, Geometry>();
function loadGeometry(name: string): Geometry {
  if (!loaded.has(name)) {
    const relative = `src/data/figures/geometry/${name}.json`;
    const absolute = path.join(process.cwd(), relative);
    if (!fs.existsSync(absolute)) throw new Error(`${relative} does not exist.`);
    loaded.set(name, JSON.parse(fs.readFileSync(absolute, 'utf-8')) as Geometry);
  }
  return loaded.get(name)!;
}

/** A drawing this much wider than tall (a row of small maps) spans the column, legend above. */
const WIDE = 1.3;

export function drawMap(spec: MapSpec): { svg: string; legends: LegendItem[][]; wide: boolean } {
  const { views, place, color, order, blank, outside, scope } = spec;
  const shapes = loadGeometry(spec.geometry);
  const ids = Object.keys(shapes.places);
  const classOf = new Map<string, string[]>(ids.map((id) => [id, []]));
  const rules: string[] = [];

  const legends = views.map((view, k) => {
    const byPlace = new Map<string, Row>();
    view.rows.forEach((row, i) => {
      const id = row[place];
      if (!(id in shapes.places)) throw new Error(`row ${i + 2}: "${id}" is not a place in ${spec.geometry}.json.`);
      if (byPlace.has(id)) throw new Error(`"${id}" appears twice in one view.`);
      byPlace.set(id, row);
    });
    const classes = classify(view.scaleRows, color, order);
    // a class code per shape: the color class, n for a blank value, x for no row
    const code = (id: string) => {
      const row = byPlace.get(id);
      if (row === undefined) return 'x';
      const i = classes.of(row);
      return i < 0 ? 'n' : String(i);
    };
    const used = new Set<string>();
    for (const id of ids) {
      const c = code(id);
      used.add(c);
      classOf.get(id)!.push(VIEW[k] + c);
    }
    // view 1 is the default; any other view wins while its switch is checked
    const when = k === 0 ? `#${scope}` : `#${scope}:has(.fig-switch label:nth-child(${k + 1}) input:checked)`;
    const fill = (c: string) => (c === 'x' ? OUTSIDE : c === 'n' ? NONE : classes.list[Number(c)].token);
    for (const c of [...used].sort()) rules.push(`${when} .${VIEW[k]}${c}{fill:${fill(c)}}`);
    return [
      ...classes.list.map(({ label: name, token }) => ({ label: name, token })),
      ...(classes.hasNone ? [{ label: blank, token: NONE }] : []),
      ...(used.has('x') ? [{ label: outside, token: OUTSIDE }] : []),
    ];
  });

  // shapes with the same class in every view become one path
  const groups = new Map<string, string[]>();
  for (const id of ids) {
    const key = classOf.get(id)!.join(' ');
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(shapes.places[id]);
  }
  const paths = [...groups].map(([key, d]) => `<path class="${key}" d="${d.join('')}"/>`).join('');
  const label = spec.label.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
  return {
    svg: `<svg viewBox="0 0 ${shapes.width} ${shapes.height}" role="img" aria-label="${label}"><style>${rules.join('')}</style>${paths}</svg>`,
    legends,
    wide: shapes.width > WIDE * shapes.height,
  };
}
