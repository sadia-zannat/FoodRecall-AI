import assert from 'node:assert/strict';
import {locales,messages,localeKeys,tr} from '../frontend/i18n.js';
const keys=localeKeys;
for(const lang of Object.keys(locales)){
 for(const key of keys){assert.equal(typeof messages[lang][key],'string',`${lang}: ${key} missing`);assert.notEqual(messages[lang][key].trim(),'');}
 const templated=['impactAnswer','conflictAnswer','evidenceAnswer','overviewAnswer'];
 for(const key of templated){const eng=[...messages.en[key].matchAll(/\{(\w+)\}/g)].map(x=>x[1]).sort();const other=[...messages[lang][key].matchAll(/\{(\w+)\}/g)].map(x=>x[1]).sort();assert.deepEqual(other,eng,`${lang}:${key} placeholder mismatch`);}
}
assert.equal(Object.keys(locales).length,8);
assert.match(tr('bn','welcomeTitle'),/পরের/);
assert.equal(tr('en','impactAnswer',{lots:'A',count:2,uncertain:'B'}).includes('{count}'),false);
console.log(`I18N PASS: ${Object.keys(locales).length} locales × ${keys.length} keys; zero missing values; template placeholders consistent.`)
