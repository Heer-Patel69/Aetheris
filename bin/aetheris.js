#!/usr/bin/env node

/**
 * Aetheris CLI Shim - npm wrapper that calls the Python CLI
 * This provides the `aetheris` command after npm install -g
 */

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

function findPython() {
  const candidates = ['python3', 'python'];
  for (const cmd of candidates) {
    try {
      execSync(`${cmd} --version`, { stdio: 'pipe' });
      return cmd;
    } catch {
      continue;
    }
  }
  return null;
}

function main() {
  const python = findPython();
  if (!python) {
    console.error('Error: Python 3.10+ is required to run Aetheris.');
    console.error('Install Python from https://python.org and try again.');
    process.exit(1);
  }

  // Check if aetheris-cli is installed
  try {
    execSync(`${python} -c "import kernel.cli"`, { stdio: 'pipe' });
  } catch {
    // Not installed, try to install it
    console.log('Aetheris CLI not found. Installing Python package...');
    const pkgDir = path.resolve(__dirname, '..');
    try {
      execSync(`${python} -m pip install -e "${pkgDir}"`, { stdio: 'inherit' });
    } catch {
      console.error('Error: Failed to install Aetheris Python package.');
      console.error(`Try: pip install -e "${pkgDir}"`);
      process.exit(1);
    }
  }

  // Forward all arguments to the Python CLI
  const args = process.argv.slice(2);
  const child = spawn(python, ['-m', 'kernel.cli', ...args], {
    stdio: 'inherit',
    env: { ...process.env, PYTHONUNBUFFERED: '1' }
  });

  child.on('close', (code) => {
    process.exit(code);
  });
}

main();
