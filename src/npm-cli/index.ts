#!/usr/bin/env node
/**
 * Aetheris CLI - npm distribution entry point
 * This is a lightweight wrapper that installs the Python runtime
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { installRuntime } from './commands/install.js';
import { startRuntime } from './commands/start.js';
import { stopRuntime } from './commands/stop.js';
import { statusRuntime } from './commands/status.js';
import { doctorRuntime } from './commands/doctor.js';
import { chatRuntime } from './commands/chat.js';
import { versionInfo } from './commands/version.js';
import { updateRuntime } from './commands/update.js';

const BANNER = `
${chalk.cyan('█████╗ ███████╗████████╗██╗  ██╗███████╗██████╗ ██╗███████╗')}
${chalk.cyan('██╔══██╗██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔══██╗██║██╔════╝')}
${chalk.cyan('███████║█████╗     ██║   ███████║█████╗  ██████╔╝██║███████╗')}
${chalk.cyan('██╔══██║██╔══╝     ██║   ██╔══██║██╔══╝  ██╔══██╗██║╚════██║')}
${chalk.cyan('██║  ██║███████╗   ██║   ██║  ██║███████╗██║  ██║██║███████║')}
${chalk.cyan('╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝')}

${chalk.bold('          AETHERIS ENGINEERING OPERATING SYSTEM')}
`;

const program = new Command();

program
  .name('aetheris')
  .description('Aetheris AI Engineering Operating System - Universal CLI')
  .version('3.1.0')
  .addHelpText('before', BANNER)
  .addHelpText('after', `
Examples:
  $ aetheris install           Install Aetheris runtime
  $ aetheris start             Start the runtime (background)
  $ aetheris start -f          Start the runtime (foreground/interactive)
  $ aetheris stop              Stop the runtime
  $ aetheris status            Show runtime status
  $ aetheris doctor            Run health checks
  $ aetheris version           Show version
  $ aetheris update            Update to latest version
  $ aetheris chat              Start interactive chat mode
  $ aetheris uninstall         Uninstall Aetheris runtime
`);

program
  .command('install')
  .description('Install Aetheris runtime')
  .option('-m, --method <method>', 'Installation method (auto, pip, python)', 'auto')
  .action(installRuntime);

program
  .command('start')
  .description('Start the Aetheris runtime')
  .option('-f, --foreground', 'Run in foreground (interactive mode)')
  .action(startRuntime);

program
  .command('stop')
  .description('Stop the Aetheris runtime')
  .action(stopRuntime);

program
  .command('status')
  .description('Show runtime status')
  .action(statusRuntime);

program
  .command('doctor')
  .description('Run installation validation')
  .action(doctorRuntime);

program
  .command('version')
  .description('Show version')
  .action(versionInfo);

program
  .command('update')
  .description('Update Aetheris to latest version')
  .action(updateRuntime);

program
  .command('chat')
  .description('Start interactive chat mode')
  .action(chatRuntime);

program
  .command('uninstall')
  .description('Uninstall Aetheris runtime')
  .action(async () => {
    const { uninstallRuntime } = await import('./commands/uninstall.js');
    await uninstallRuntime();
  });

// Default: show banner and help if no command
if (!process.argv.slice(2).length) {
  console.log(BANNER);
  console.log(chalk.bold('Version :'), '3.1.0');
  console.log(chalk.bold('Runtime :'), 'Ready');
  console.log(chalk.bold('Brain   :'), 'Ready');
  console.log(chalk.bold('Skills  :'), 'Loaded');
  console.log(chalk.bold('Memory  :'), 'Ready');
  console.log(chalk.bold('Status  :'), 'Waiting for Requests');
  console.log();
  program.outputHelp();
  process.exit(0);
}

program.parse(process.argv);