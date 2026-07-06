#!/usr/bin/env node

/**
 * postinstall script for npm package aetheris
 * Ensures the Python CLI is installed in the user's environment
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

function findPython() {
  const candidates = process.platform === 'win32'
    ? ['python', 'python3', 'py -3']
    : ['python3', 'python'];
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
    console.warn('Warning: Python 3.10+ not found. Aetheris requires Python.');
    console.warn('Install Python from https://python.org and run: npm run postinstall');
    process.exit(0);
  }

  const pkgDir = path.resolve(__dirname, '..');
  console.log(`Installing Aetheris Python CLI from ${pkgDir}...`);

  try {
    // Try editable install first (for local development)
    execSync(`${python} -m pip install -e "${pkgDir}" 2>&1 || ${python} -m pip install "${pkgDir}"`, {
      stdio: 'inherit',
      shell: true,
      timeout: 120000,
    });
    console.log('Aetheris Python CLI installed successfully.');
  } catch (e) {
    console.warn('Warning: Could not auto-install Python package.');
    console.warn(`Try: pip install -e "${pkgDir}"`);
    console.warn(`Or: npm install -g aetheris`);
  }
}

main();
