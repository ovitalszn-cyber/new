import { cpSync, existsSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendDir = dirname(fileURLToPath(import.meta.url));
const rootDir = join(frontendDir, '..');

const COPY_PATHS = [
  'app',
  'components',
  'lib',
  'public',
  'data',
  'middleware.ts',
  'next.config.ts',
  'tsconfig.json',
  'postcss.config.mjs',
  'eslint.config.mjs',
];

for (const relativePath of COPY_PATHS) {
  const source = join(rootDir, relativePath);
  const target = join(frontendDir, relativePath);

  if (!existsSync(source)) {
    continue;
  }

  rmSync(target, { recursive: true, force: true });
  cpSync(source, target, { recursive: true });
}
