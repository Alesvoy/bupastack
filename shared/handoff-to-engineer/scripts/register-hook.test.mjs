import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { chmodSync, mkdtempSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

const script = fileURLToPath(new URL('register-hook.mjs', import.meta.url))
const checker = fileURLToPath(new URL('check-kickoff.mjs', import.meta.url))
const herdr = { hooks: [{ type: 'command', command: '/Users/alesvoy/.local/libexec/herdr-agent-notify claude', timeout: 5 }] }
const kickoffEntry = {
  matcher: 'mcp__t3-code__t3_thread_launch|mcp__t3-code__t3_thread_send',
  hooks: [{ type: 'command', command: `"${process.execPath}" "${checker}"`, timeout: 10 }],
}

const tempSettings = (content) => {
  const file = join(mkdtempSync(join(tmpdir(), 'register-hook-')), 'settings.json')
  if (content !== undefined) writeFileSync(file, content)
  return file
}
const register = (file, nodeBin = '') =>
  spawnSync(process.execPath, [script], { env: { ...process.env, CLAUDE_SETTINGS: file, NODE_BIN: nodeBin }, encoding: 'utf8' })

test('registers one kickoff entry beside the herdr entry, however often it runs', () => {
  const file = tempSettings(JSON.stringify({ model: 'opus', hooks: { PreToolUse: [herdr], Stop: [herdr] } }))
  assert.equal(register(file).status, 0)
  assert.equal(register(file).status, 0)
  const text = readFileSync(file, 'utf8')
  assert.ok(text.endsWith('}\n'))
  assert.deepEqual(JSON.parse(text), { model: 'opus', hooks: { PreToolUse: [herdr, kickoffEntry], Stop: [herdr] } })
})

test('keeps the settings file private', () => {
  const file = tempSettings('{}')
  chmodSync(file, 0o600)
  assert.equal(register(file).status, 0)
  assert.equal(statSync(file).mode & 0o777, 0o600)
})

test('creates the settings file when it is missing', () => {
  const file = tempSettings()
  assert.equal(register(file).status, 0)
  assert.deepEqual(JSON.parse(readFileSync(file, 'utf8')), { hooks: { PreToolUse: [kickoffEntry] } })
})

test('aborts on invalid JSON and leaves the file alone', () => {
  const file = tempSettings('{ "hooks": ')
  const result = register(file)
  assert.equal(result.status, 1)
  assert.match(result.stderr, /^Not registering the kickoff hook\. .*settings\.json is not a valid settings file: /)
  assert.equal(readFileSync(file, 'utf8'), '{ "hooks": ')
})

test('uses the node path from NODE_BIN, so a node upgrade keeps the hook working', () => {
  const file = tempSettings('{}')
  assert.equal(register(file, '/opt/homebrew/bin/node').status, 0)
  assert.equal(JSON.parse(readFileSync(file, 'utf8')).hooks.PreToolUse[0].hooks[0].command, `"/opt/homebrew/bin/node" "${checker}"`)
})
