import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { chmodSync, mkdtempSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

const script = fileURLToPath(new URL('register-hook.mjs', import.meta.url))
const checker = fileURLToPath(new URL('check-kickoff.mjs', import.meta.url))
const otherHook = { type: 'command', command: '/usr/local/bin/other-hook', timeout: 5 }
const other = { hooks: [otherHook] }
const kickoffHook = { type: 'command', command: `"${process.execPath}" "${checker}"`, timeout: 10 }
const kickoffEntry = { matcher: 'mcp__t3-code__t3_thread_launch', hooks: [kickoffHook] }
const oldMatcher = 'mcp__t3-code__t3_thread_launch|mcp__t3-code__t3_thread_send'

const tempSettings = (content) => {
  const file = join(mkdtempSync(join(tmpdir(), 'register-hook-')), 'settings.json')
  if (content !== undefined) writeFileSync(file, content)
  return file
}
const register = (file, nodeBin = '') =>
  spawnSync(process.execPath, [script], { env: { ...process.env, CLAUDE_SETTINGS: file, NODE_BIN: nodeBin }, encoding: 'utf8' })

test('registers one kickoff entry beside an unrelated entry, however often it runs', () => {
  const file = tempSettings(JSON.stringify({ model: 'opus', hooks: { PreToolUse: [other], Stop: [other] } }))
  assert.equal(register(file).status, 0)
  assert.equal(register(file).status, 0)
  const text = readFileSync(file, 'utf8')
  assert.ok(text.endsWith('}\n'))
  assert.deepEqual(JSON.parse(text), { model: 'opus', hooks: { PreToolUse: [other, kickoffEntry], Stop: [other] } })
})

test('keeps an unrelated hook that shares an entry with an old kickoff hook', () => {
  const file = tempSettings(JSON.stringify({ hooks: { PreToolUse: [{ matcher: oldMatcher, hooks: [otherHook, kickoffHook] }] } }))
  assert.equal(register(file).status, 0)
  assert.deepEqual(JSON.parse(readFileSync(file, 'utf8')), { hooks: { PreToolUse: [{ matcher: oldMatcher, hooks: [otherHook] }, kickoffEntry] } })
})

test('migrates an old launch-and-send kickoff entry to one launch-only entry', () => {
  const file = tempSettings(JSON.stringify({ hooks: { PreToolUse: [{ matcher: oldMatcher, hooks: [kickoffHook] }] } }))
  assert.equal(register(file).status, 0)
  assert.deepEqual(JSON.parse(readFileSync(file, 'utf8')), { hooks: { PreToolUse: [kickoffEntry] } })
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

for (const [shape, content] of [
  ['a hooks value that is not an object', '{"hooks":"oops"}'],
  ['a PreToolUse value that is not an array', '{"hooks":{"PreToolUse":{"matcher":"x"}}}'],
]) {
  test(`aborts on ${shape} and leaves the file alone`, () => {
    const file = tempSettings(content)
    const result = register(file)
    assert.equal(result.status, 1)
    assert.match(result.stderr, /^Not registering the kickoff hook\. .*settings\.json is not a valid settings file: /)
    assert.equal(readFileSync(file, 'utf8'), content)
  })
}
