// news-17-nov — entrypoint for the make.fun news-image-20261117 bounty.
// Copies the pre-rendered entry.png (see draw_infographic.py) into the
// output directory so the judges receive exactly the verified image.
import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const src = join(here, "entry.png");

if (!existsSync(src)) {
  throw new Error(`entry.png not found next to main.ts (${src})`);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(src, join(outDir, "entry.png"));
console.log(
  `entry.png (${statSync(src).size} bytes) written to ${join(outDir, "entry.png")}`,
);
