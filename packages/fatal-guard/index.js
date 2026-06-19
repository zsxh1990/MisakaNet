#!/usr/bin/env node
/**
 * @misaka-net/fatal-guard
 *
 * Zero-dependency non-invasive fatal error guard.
 *
 * This module exports:
 *   - buildPayload(reason)  — Build a 4-field JSON payload
 *   - runHandler(reason)    — Fire the external handler (if FATAL_HANDLER is set)
 *   - FatalPayload          — Type signature (JSDoc)
 *
 * For automatic hook registration, use:
 *   node -r @misaka-net/fatal-guard/register ./app.js
 *
 * Or import and attach manually:
 *   const { runHandler } = require('@misaka-net/fatal-guard');
 *   process.on('uncaughtException', (err) => runHandler('uncaught_exception'));
 */

const { spawn } = require('node:child_process');

/**
 * @typedef {Object} FatalPayload
 * @property {number} schemaVersion — Payload format version (always 1)
 * @property {string} reason — "uncaught_exception" | "unhandled_rejection" | "exit_code"
 * @property {string} timestamp — ISO 8601 timestamp
 * @property {number} pid — Process ID
 */

/** Build a 4-field JSON payload string. @param {string} reason @returns {string} */
function buildPayload(reason) {
  return JSON.stringify({
    schemaVersion: 1,
    reason,
    timestamp: new Date().toISOString(),
    pid: process.pid,
  });
}

/**
 * Fire-and-forget external handler invocation.
 * Reads FATAL_HANDLER env var (or fallback chain), spawns with JSON payload as argv[1].
 * Never throws. Never blocks shutdown.
 *
 * @param {string} reason
 * @param {string} [customPayload] — optional pre-built JSON payload (wrapper mode passes extra fields)
 */
function runHandler(reason, customPayload) {
  const handler = (
    process.env.FATAL_HANDLER ||
    process.env.MISAKANET_ERROR_HANDLER ||
    process.env.VITE_ERROR_HANDLER ||
    process.env.E2B_ERROR_HANDLER ||
    process.env.OPENCLAW_ERROR_HANDLER ||
    ''
  ).trim();
  if (!handler) return;

  try {
    const payload = customPayload || buildPayload(reason);
    const child = spawn(handler, [payload], {
      stdio: 'ignore',
      detached: true,
      shell: false,
    });
    child.on('error', () => {});
    child.unref();
  } catch (_) {}
}

module.exports = { buildPayload, runHandler };
