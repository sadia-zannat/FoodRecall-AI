import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../frontend/app.js',import.meta.url),'utf8');
const m=source.match(/const v02=(\{[\s\S]*?\});\s*const v02Keys=(\[[^\n]+\]);/);
assert.ok(m,'V0.2 dictionary and keys must be present');
const dict=vm.runInNewContext('('+m[1]+')');
const keys=vm.runInNewContext(m[2]);
assert.equal(Object.keys(dict).length,8);
for(const [lang,translations] of Object.entries(dict)){
 assert.equal(translations.length,keys.length,`${lang} missing V0.2 UI keys`);
 assert.ok(translations.every(x=>typeof x==='string'&&x.trim()),`${lang} has empty translation`);
}
console.log(`V0.2 I18N PASS: 8 locales × ${keys.length} new strings`);
