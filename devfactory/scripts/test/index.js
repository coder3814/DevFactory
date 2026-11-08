'use strict';

// Lets `node --test devfactory/scripts/test` run every *.test.js here: Node resolves the
// folder to this file, which loads the test files into one run.

const fs = require('fs');
const path = require('path');

for (const name of fs.readdirSync(__dirname).sort()) {
  if (name.endsWith('.test.js')) require(path.join(__dirname, name));
}
