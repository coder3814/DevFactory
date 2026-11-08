// Lets `node --test devfactory/hooks/test` run every hook test: Node resolves a directory
// argument to its index.js, which loads each *.test.js file here.
'use strict';

const fs = require('fs');
const path = require('path');

for (const name of fs.readdirSync(__dirname).filter((n) => n.endsWith('.test.js')).sort()) {
  require(path.join(__dirname, name));
}
