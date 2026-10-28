import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

const script = fileURLToPath(new URL('check-kickoff.mjs', import.meta.url))
const dir = mkdtempSync(join(tmpdir(), 'check-kickoff-'))
const skill = join(dir, 'engineer', 'SKILL.md')
const ticket = join(dir, 'ticket.md')
mkdirSync(join(dir, 'engineer'))
writeFileSync(skill, '')
writeFileSync(ticket, '')

const kickoff = ({ skillPath = skill, ticketPath = ticket, thread = 'thread-123' } = {}) =>
  `You are the engineer for this ticket. Follow the engineer skill at ${skillPath}.\nTicket: ${ticketPath}\nCoordinator thread: ${thread}`

const run = (input) => spawnSync(process.execPath, [script], { input, encoding: 'utf8' })
const launch = (tool_input) => run(JSON.stringify({ tool_name: 'mcp__t3-code__t3_thread_launch', tool_input }))
const send = (message) => run(JSON.stringify({ tool_name: 'mcp__t3-code__t3_thread_send', tool_input: { threadId: 't', message } }))

const allowed = (result) => assert.deepEqual([result.status, result.stdout, result.stderr], [0, '', ''])
const rejected = (result, problem) => {
  assert.equal(result.status, 2)
  assert.equal(result.stdout, '')
  assert.ok(result.stderr.includes(`\n- ${problem}\n`), result.stderr)
}

test('allows a valid kickoff', () => allowed(launch({ title: 'Engineer ABC-1', message: kickoff() })))
test('allows a valid kickoff with CRLF line endings', () => allowed(launch({ title: 'Engineer', message: kickoff().replaceAll('\n', '\r\n') })))
test('allows a launch that is not an engineer kickoff', () => allowed(launch({ title: 'Research', message: 'Look into the flaky test.' })))
test('allows a rework message sent to an engineer', () => allowed(send('Review found two issues. Fix them and push.')))
test('allows a launch with no message', () => allowed(launch({ title: 'Engineer ABC-1', message: null })))
test('allows empty stdin', () => allowed(run('')))
test('allows an answer that quotes the kickoff', () =>
  allowed(send('Your kickoff said "You are the engineer for this ticket" plus "Also refactor the header." Skip the header line.')))
test('allows a launch that names the engineering coordinator', () =>
  allowed(launch({ title: 'Engineering coordinator', message: 'You are the engineering coordinator for the orders app. Hand off the ready tickets.' })))

test('rejects an extra line with the template and a pointer to the ticket', () => {
  const result = launch({ title: 'Engineer ABC-1', message: `${kickoff()}\nAlso refactor the header.` })
  assert.equal(result.status, 2)
  assert.equal(result.stdout, '')
  assert.equal(
    result.stderr,
    `Engineer kickoff rejected.
- The kickoff has 4 lines. It must have exactly 3.

Send exactly these 3 lines, with only the placeholders filled:
You are the engineer for this ticket. Follow the engineer skill at <engineer skill path>.
Ticket: <ticket path>
Coordinator thread: <coordinator thread ID>

Put every other instruction, link, or constraint in the ticket, not the kickoff.
`,
  )
})

test('rejects a paraphrased first line', () =>
  rejected(
    launch({ title: 'Build it', message: `You're our engineer, read ${skill}.\nTicket: ${ticket}\nCoordinator thread: t1` }),
    'Line 1 does not match the template.',
  ))

test('rejects a free-form message under an Engineer title', () =>
  rejected(launch({ title: 'Engineer foo', message: 'Please build the login page.' }), 'Line 1 does not match the template.'))

test('rejects a relative skill path', () =>
  rejected(
    launch({ title: 'Engineer', message: kickoff({ skillPath: 'shared/engineer/SKILL.md' }) }),
    'The engineer skill path "shared/engineer/SKILL.md" is not absolute.',
  ))

test('rejects a ~ ticket path and says to expand it', () =>
  rejected(
    launch({ title: 'Engineer', message: kickoff({ ticketPath: '~/.agents/tickets/a.md' }) }),
    'The ticket path "~/.agents/tickets/a.md" starts with ~. Expand it to an absolute path.',
  ))

test('rejects a ticket file that does not exist', () =>
  rejected(
    launch({ title: 'Engineer', message: kickoff({ ticketPath: join(dir, 'missing.md') }) }),
    `The ticket path "${join(dir, 'missing.md')}" does not exist.`,
  ))

test('rejects an off-template kickoff sent with t3_thread_send', () =>
  rejected(send(`${kickoff()}\nAlso refactor the header.`), 'The kickoff has 4 lines. It must have exactly 3.'))

test('rejects a send that opens with another line before the kickoff', () =>
  rejected(send(`Please start here.\n${kickoff()}\nAlso refactor the header.`), 'The kickoff has 5 lines. It must have exactly 3.'))

test('rejects a paraphrased send that has a Coordinator thread line', () =>
  rejected(send(`You're our engineer, read ${skill}.\nTicket: ${ticket}\nCoordinator thread: t1`), 'Line 1 does not match the template.'))

test('rejects an off-template kickoff whose tool_name is not a string', () =>
  rejected(
    run(JSON.stringify({ tool_name: 42, tool_input: { title: 'Engineer', message: `${kickoff()}\nAlso refactor the header.` } })),
    'The kickoff has 4 lines. It must have exactly 3.',
  ))
