import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const js=readFileSync('frontend/app.js','utf8');
const css=readFileSync('frontend/styles.css','utf8');
// Public UI must not expose internal checkpoint identifiers.
for (const token of [' · V0.8','v0.8 •','FOODRECALL AI · V0.8']) assert.ok(!js.includes(token),`Internal checkpoint leaked into user-facing UI: ${token}`);
assert.ok(js.includes('<span class="brand-main">FoodRecall <em>AI</em></span>'));
assert.ok(js.includes('Evidence-based recall investigation'));
assert.ok(js.includes("esc(l('trainingMode'))"),'Safety label should remain');
assert.match(css,/\.login-card \.brand-main\{color:#172a39\}/,'Login branding must be readable on white');
assert.match(css,/\.login-card \.brand-main em\{color:#087c73\}/,'AI part must remain readable');
console.log('PASS: no internal checkpoint in visible UI, login contrast fix present, demo label retained.');
