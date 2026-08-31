import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const template = fs.readFileSync(path.resolve(__dirname, '../assets/template.html'), 'utf8');

test('toolbar uses absolute positioning on desktop to prevent canvas overlap during scroll', () => {
  assert.match(template, /\.toolbar \{[\s\S]*?position: absolute;[\s\S]*?top: 1rem;[\s\S]*?right: 1rem;[\s\S]*?gap: 0\.5rem;/);
  assert.match(template, /html\[data-present="true"\]:not\(\[data-embed="true"\]\) \.toolbar \{[\s\S]*?position: absolute;/);
});

test('Archify.guidedViews implements step-by-step keyboard navigation and zoom-focus toggle', () => {
  assert.match(template, /function nextStep\(\)/);
  assert.match(template, /function prevStep\(\)/);
  assert.match(template, /function toggleZoomFocus\(\)/);
  assert.match(template, /nextStep: nextStep,/);
  assert.match(template, /prevStep: prevStep,/);
  assert.match(template, /toggleZoomFocus: toggleZoomFocus,/);
});

test('Archify.routeProbe exports nextJourney and previousJourney for flow traversal', () => {
  assert.match(template, /nextJourney: nextJourney,/);
  assert.match(template, /previousJourney: previousJourney,/);
});

test('global keydown listener handles step navigation and Enter zoom toggle without conflicting with input fields', () => {
  assert.match(template, /e\.key === 'ArrowRight' \|\| e\.key === 'j' \|\| e\.key === 'J' \|\| e\.key === 'n' \|\| e\.key === 'N'/);
  assert.match(template, /e\.key === 'ArrowLeft' \|\| e\.key === 'k' \|\| e\.key === 'K' \|\| e\.key === 'b' \|\| e\.key === 'B'/);
  assert.match(template, /e\.key === 'Enter'/);
  assert.match(template, /Archify\.guidedViews\.toggleZoomFocus\(\)/);
});

test('diagram guide shortcuts display step navigation and zoom-focus hotkeys', () => {
  assert.match(template, /<kbd>← \/ →<\/kbd> \{\{i18n:viewer\.guide\.shortcut\.stepNav\}\}/);
  assert.match(template, /<kbd>Enter<\/kbd> \{\{i18n:viewer\.guide\.shortcut\.zoomFocus\}\}/);
});
