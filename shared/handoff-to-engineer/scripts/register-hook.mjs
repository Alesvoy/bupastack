import { existsSync, mkdirSync, readFileSync, renameSync, statSync, writeFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const file = process.env.CLAUDE_SETTINGS || join(homedir(), '.claude', 'settings.json')
const node = process.env.NODE_BIN || process.execPath
const script = fileURLToPath(new URL('check-kickoff.mjs', import.meta.url))

const isObject = (value) => typeof value === 'object' && value !== null && !Array.isArray(value)
let settings
try {
  settings = existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : {}
  if (!isObject(settings)) throw new Error('not a JSON object')
  settings.hooks ??= {}
  if (!isObject(settings.hooks)) throw new Error('"hooks" is not a JSON object')
  settings.hooks.PreToolUse ??= []
  if (!Array.isArray(settings.hooks.PreToolUse)) throw new Error('"hooks.PreToolUse" is not an array')
} catch (error) {
  console.error(`Not registering the kickoff hook. ${file} is not a valid settings file: ${error.message}`)
  process.exit(1)
}

const ours = (hook) => String(hook?.command).includes('check-kickoff.mjs')
const withoutOurs = (entry) => {
  if (!Array.isArray(entry?.hooks) || !entry.hooks.some(ours)) return [entry]
  const hooks = entry.hooks.filter((hook) => !ours(hook))
  return hooks.length ? [{ ...entry, hooks }] : []
}
settings.hooks.PreToolUse = [
  ...settings.hooks.PreToolUse.flatMap(withoutOurs),
  {
    matcher: 'mcp__t3-code__t3_thread_launch',
    // Absolute node path, because apps launched from the macOS GUI often lack Homebrew on PATH.
    hooks: [{ type: 'command', command: `"${node}" "${script}"`, timeout: 10 }],
  },
]

mkdirSync(dirname(file), { recursive: true })
const temp = `${file}.${process.pid}.tmp`
const mode = existsSync(file) ? statSync(file).mode & 0o777 : 0o600
writeFileSync(temp, `${JSON.stringify(settings, null, 2)}\n`, { mode })
renameSync(temp, file)
console.log(`Registered ${script} as a PreToolUse hook in ${file}`)
