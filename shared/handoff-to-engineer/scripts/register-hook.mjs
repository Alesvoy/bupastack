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
  if (!isObject(settings.hooks ?? {})) throw new Error('"hooks" is not a JSON object')
  if (!Array.isArray(settings.hooks?.PreToolUse ?? [])) throw new Error('"hooks.PreToolUse" is not an array')
} catch (error) {
  console.error(`Not registering the kickoff hook. ${file} is not a valid settings file: ${error.message}`)
  process.exit(1)
}

const ours = (entry) => entry?.hooks?.some?.((hook) => String(hook?.command).includes('check-kickoff.mjs'))
settings.hooks ??= {}
settings.hooks.PreToolUse = [
  ...(settings.hooks.PreToolUse ?? []).filter((entry) => !ours(entry)),
  {
    matcher: 'mcp__t3-code__t3_thread_launch|mcp__t3-code__t3_thread_send',
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
