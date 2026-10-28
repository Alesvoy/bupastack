import { existsSync, readFileSync } from 'node:fs'
import { isAbsolute } from 'node:path'

const template = `You are the engineer for this ticket. Follow the engineer skill at <engineer skill path>.
Ticket: <ticket path>
Coordinator thread: <coordinator thread ID>`

const pathProblem = (name, suffix) => (path) => {
  if (path.startsWith('~')) return `The ${name} "${path}" starts with ~. Expand it to an absolute path.`
  if (!isAbsolute(path)) return `The ${name} "${path}" is not absolute.`
  if (!path.endsWith(suffix)) return `The ${name} "${path}" does not end in ${suffix}.`
  if (!existsSync(path)) return `The ${name} "${path}" does not exist.`
}

const checks = [
  pathProblem('engineer skill path', '/engineer/SKILL.md'),
  pathProblem('ticket path', '.md'),
  (id) => (id.trim() ? undefined : 'The coordinator thread ID is empty.'),
]
const escape = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
const lines = template.split('\n').map((line, i) => ({
  pattern: new RegExp(`^${escape(line).replace(/<[^>]+>/g, '(.*)')}$`),
  check: checks[i],
}))
if (checks.length !== lines.length) throw new Error('check-kickoff.mjs needs one check per template line.')

const problems = (message) => {
  const sent = message.trimEnd().split(/\r?\n/)
  const found = sent.length === lines.length ? [] : [`The kickoff has ${sent.length} lines. It must have exactly ${lines.length}.`]
  lines.forEach(({ pattern, check }, i) => {
    const match = sent[i]?.match(pattern)
    const problem = match ? check(match[1]) : `Line ${i + 1} does not match the template.`
    if (problem) found.push(problem)
  })
  return found
}

let call
try {
  call = JSON.parse(readFileSync(0, 'utf8'))
} catch {
  process.exit(0)
}
const { title, message } = call?.tool_input ?? {}
const text = typeof message === 'string' ? message : ''
if (!/^Engineer\b/.test(title) && !/You are the engineer\b/.test(text) && !/^\s*Coordinator thread:/m.test(text)) process.exit(0)

const found = text.trim() ? problems(text) : ['The kickoff must be in the launch message.']
if (found.length) {
  process.stderr.write(`Engineer kickoff rejected.
${found.map((p) => `- ${p}`).join('\n')}

Send exactly these ${lines.length} lines, with only the placeholders filled:
${template}

Put every other instruction, link, or constraint in the ticket, not the kickoff.
`)
  process.exit(2)
}
