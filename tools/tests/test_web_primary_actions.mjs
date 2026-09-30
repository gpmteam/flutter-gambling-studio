import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../web_verify.mjs', import.meta.url), 'utf8');

function sourcePattern(name) {
  const match = source.match(new RegExp(`const ${name} = \/(.*)\/([a-z]*);`));
  assert.ok(match, `${name} is declared in the verifier`);
  return new RegExp(match[1], match[2]);
}

const start = source.indexOf('function findByLabel(');
const end = source.indexOf('\n}', start) + 2;
assert.ok(start >= 0 && end > start, 'Verifier exposes its label matcher');
const findByLabel = vm.runInNewContext(`(${source.slice(start, end)})`);

test('menu matcher skips merged instructions and the How to Play link', () => {
  const play = sourcePattern('PRIMARY_PLAY_LABEL');
  const nodes = [
    {label: 'A jewel carnival PLAY CLASSIC How to Play'},
    {label: 'How to Play'},
    {label: 'PLAY CLASSIC'},
  ];
  assert.equal(findByLabel(nodes, play).label, 'PLAY CLASSIC');
});

test('game action matcher selects the shoot control and not a merged route label', () => {
  const action = sourcePattern('PRIMARY_ACTION_LABEL');
  const nodes = [
    {label: 'Back Joker Jewels SCORE 1000 How to play'},
    {label: 'Spotlight · 25'},
    {label: 'SHOOT • 5'},
  ];
  assert.equal(findByLabel(nodes, action).label, 'SHOOT • 5');
});

test('help text alone is not treated as a play action', () => {
  const play = sourcePattern('PRIMARY_PLAY_LABEL');
  assert.equal(findByLabel([{label: 'How to Play'}], play), undefined);
});
