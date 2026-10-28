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

const problems = (message) => {
  const sent = message.trim().split(/\r?\n/)
  const found = sent.length === lines.length ? [] : [`The kickoff has ${sent.length} lines. It must have exactly ${lines.length}.`]
  lines.forEach(({ pattern, check }, i) => {
    const match = sent[i]?.match(pattern)
    const problem = match ? check(match[1]) : `Line ${i + 1} does not match the template.`
    if (problem) found.push(problem)
  })
  return found
}

const kickoffLineStart = /^(You are the engineer\b|Coordinator thread:)/m
const isKickoff = ({ tool_name, tool_input: { message, title } }) =>
  (String(tool_name).endsWith('t3_thread_launch') && /^Engineer\b/.test(title)) || kickoffLineStart.test(message)

let call
try {
  call = JSON.parse(readFileSync(0, 'utf8'))
} catch {
  process.exit(0)
}
if (typeof call?.tool_input?.message !== 'string' || !isKickoff(call)) process.exit(0)

const found = problems(call.tool_input.message)
if (found.length) {
  process.stderr.write(`Engineer kickoff rejected.
${found.map((p) => `- ${p}`).join('\n')}

Send exactly these ${lines.length} lines, with only the placeholders filled:
${template}

Put every other instruction, link, or constraint in the ticket, not the kickoff.
`)
  process.exit(2)
}
