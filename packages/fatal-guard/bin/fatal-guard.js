#!/usr/bin/env node
/**
 * @misaka-net/fatal-guard — CLI wrapper mode
 *
 * Usage:
 *   npx @misaka-net/fatal-guard -- <command> [args...]
 *   FATAL_HANDLER=/usr/bin/logger npx @misaka-net/fatal-guard -- node app.js
 *
 * Spawns the command as a child process, monitors stderr and exit code,
 * fires the external handler on non-zero exit with crash signal.
 */

const { spawn } = require('node:child_process');

const args = process.argv.slice(2);

if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
  console.error(`
Usage:
  FATAL_HANDLER=/usr/bin/logger npx @misaka-net/fatal-guard -- <command> [args...]

Examples:
  npx @misaka-net/fatal-guard -- node app.js
  FATAL_HANDLER=/usr/bin/logger npx @misaka-net/fatal-guard -- ./node_modules/.bin/vite build

Wraps any Node.js CLI with fatal error monitoring — zero source code changes.
`);
  process.exit(args.length === 0 ? 1 : 0);
}

// Remove leading `--` if present (allows `fatal-guard -- cmd` syntax)
let cmdArgs = args;
if (cmdArgs[0] === '--') {
  cmdArgs = cmdArgs.slice(1);
}

if (cmdArgs.length === 0) {
  console.error('fatal-guard: missing command after --');
  process.exit(1);
}

const { buildPayload, runHandler } = require('./index');

const child = spawn(cmdArgs[0], cmdArgs.slice(1), {
  stdio: ['inherit', 'inherit', 'pipe'],
  shell: false,
});

let stderrBuffer = '';
child.stderr.on('data', (chunk) => {
  stderrBuffer += chunk.toString();
  process.stderr.write(chunk); // pass through to user terminal
});

child.on('exit', (code, signal) => {
  const crashed = code !== 0 && code !== null;
  const hasError = /error|exception|traceback|failed|fatal|killed/i.test(stderrBuffer);

  if (crashed && hasError) {
    const reason = signal ? `killed_by_${signal}` : 'process_crash';
    try {
      // Extend payload with a snippet of the last stderr lines
      const snippet = stderrBuffer.split('\n').filter(Boolean).slice(-4).join('\n').trim();
      const payload = JSON.stringify({
        ...JSON.parse(buildPayload(reason)),
        snippet: snippet.slice(0, 500),
      });
      runHandler(reason, payload);
    } catch (_) {}
  }

  process.exit(code ?? 1);
});

child.on('error', () => {
  process.exit(1);
});
