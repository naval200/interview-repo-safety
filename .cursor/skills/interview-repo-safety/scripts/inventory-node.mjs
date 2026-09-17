#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');
const root = path.resolve(process.argv[2] || '.');
const pkgPath = path.join(root, 'package.json');

function classifySource(spec) {
  const s = String(spec);
  if (s.startsWith('git+') || s.includes('github.com') || s.startsWith('git://')) return 'git';
  if (/^https?:\/\//.test(s) && /\.tgz|\.tar\.gz|tarball/i.test(s)) return 'tarball';
  if (s.startsWith('file:') || s.startsWith('.') || s.startsWith('/')) return 'file';
  if (s.startsWith('npm:')) return 'alias';
  return 'registry';
}

if (!fs.existsSync(pkgPath)) {
  console.log(JSON.stringify({ error: 'no package.json', root }, null, 2));
  process.exit(0);
}

const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
const sections = ['dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies'];
const entries = [];
for (const section of sections) {
  for (const [name, version] of Object.entries(pkg[section] || {})) {
    entries.push({
      name,
      version,
      directOrTransitive: 'direct',
      dependencyType: section,
      parent: null,
      source: classifySource(version),
      privateScope: name.startsWith('@') && name.includes('/'),
      unusualSource: classifySource(version) !== 'registry',
    });
  }
}

const lockCandidates = [
  'package-lock.json', 'npm-shrinkwrap.json', 'pnpm-lock.yaml',
  'yarn.lock', 'bun.lock', 'bun.lockb',
];
const lifecycle = {};
for (const key of ['preinstall','install','postinstall','prepare','prepublish','prepack','prepublishOnly']) {
  if (pkg.scripts && pkg.scripts[key]) lifecycle[key] = pkg.scripts[key];
}

console.log(JSON.stringify({
  root,
  name: pkg.name || null,
  workspaces: pkg.workspaces || null,
  lockfiles: lockCandidates.filter((f) => fs.existsSync(path.join(root, f))),
  note: 'Transitive deps require lockfile parse; mark not verified if absent.',
  directDependencies: entries,
  lifecycleScripts: lifecycle,
  npmrcPresent: fs.existsSync(path.join(root, '.npmrc')),
}, null, 2));
