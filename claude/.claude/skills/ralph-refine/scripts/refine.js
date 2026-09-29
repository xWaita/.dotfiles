export const meta = {
  name: 'ralph-refine',
  description: 'Loop ai-review -> fix -> ai-compact over a plan until no Critical/High/Medium findings remain',
  phases: [
    { title: 'Review+fix', detail: 'ai-review, then resolve its findings' },
    { title: 'Compact+record', detail: 'ai-compact, append the round to the ledger, commit' },
  ],
}

// args: {files: string[] (absolute), maxRounds: number, ledgerPath: string (absolute),
//        firstRound: number, firstId: number — 1 and 1 for a new ledger, else one past the committed ledger's highest}
// The agents' instructions live in ../references/; this script only sequences them and renders the ledger entries.
const { files, maxRounds = 50, ledgerPath, firstRound = 1, firstId = 1 } = args
const REFS = '~/.claude/skills/ralph-refine/references'
const BLOCKING = ['CRITICAL', 'HIGH', 'MEDIUM']
const common = { files: files.join(', '), ledgerPath }

const obj = properties => ({ type: 'object', properties, required: Object.keys(properties) })
const str = description => ({ type: 'string', description })

const REVIEW_FIX = obj({
  findings: {
    type: 'array',
    items: obj({
      id: str('F<n>, numbered in order from the start id given'),
      severity: { enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] },
      impact: { enum: ['unrecoverable', 'severe', 'moderate', 'minor'] },
      exposure: { enum: ['high', 'medium', 'low'] },
      location: str('repo-relative plan file:line, as reviewed before any edit'),
      flaw: str('one sentence'),
      status: { enum: ['applied', 'declined', 'conflict'] },
      change: str('applied: one sentence, at most ~30 words, stating what the plan now says (not what you did); else empty'),
      reason: str('declined/conflict: why, naming the conflicting F# if any; else empty'),
    }),
  },
  intentQuestions: { type: 'array', items: { type: 'string' } },
})

const block = (name, text) => `<<<${name}\n${text}\n${name}>>>`
const instruct = (file, params, ...blocks) =>
  [`Read ${REFS}/${file} and follow it as your instructions.\n\nParameters:\n` +
    Object.entries(params).map(([k, v]) => `- ${k}: ${v}`).join('\n'), ...blocks].join('\n\n')

// agent() yields null when it dies on an API error after retries; fail the run — earlier rounds are committed.
async function run(prompt, opts) {
  const result = await agent(prompt, opts)
  if (!result) throw new Error(`${opts.label} failed; every earlier round is committed`)
  return result
}

function renderEntry(e) {
  const head = `- ${e.id} · ${e.severity} (${e.impact}·${e.exposure}) · ${e.status} — ${e.location}: ${e.flaw}`
  if (e.status === 'applied') return `${head} Now: ${e.change}`
  if (e.status === 'conflict') return `${head} Needs your call: ${e.reason}`
  return `${head} Why: ${e.reason}`
}

let nextId = firstId
let stopReason = 'cap'
let intentQuestions = []

for (let n = firstRound; n < firstRound + maxRounds; n++) {
  const review = await run(
    instruct('review.md', { ...common, firstId: nextId }),
    { label: `review+fix:r${n}`, phase: 'Review+fix', schema: REVIEW_FIX, effort: 'high' },
  )
  intentQuestions = review.intentQuestions

  // Renumber by position so ids stay contiguous whatever the agent wrote.
  const findings = review.findings.map(f => ({ ...f, id: `F${nextId++}` }))
  const blocking = findings.filter(f => BLOCKING.includes(f.severity))
  const applied = findings.filter(f => f.status === 'applied')
  log(`round ${n}: ${blocking.length} blocking, ${findings.length - blocking.length} low, ${applied.length} applied`)
  if (!findings.length) { stopReason = 'converged'; break }

  // A round that applied nothing is still recorded, so a rerun does not re-raise its declined findings.
  const message = [`plan: refine round ${n}`, '', ...findings.map(e => `${e.id} ${e.severity} ${e.status}${e.change ? `: ${e.change}` : ''}`)]
  await run(
    instruct('record.md', { ...common, round: n },
      block('FIXES', applied.map(e => `- ${e.id}: ${e.change}`).join('\n')),
      block('LEDGER', findings.map(renderEntry).join('\n')),
      block('MSG', message.join('\n'))),
    { label: `compact+record:r${n}`, phase: 'Compact+record' },
  )

  // Lows are fixed when they are an easy win but never keep the loop running.
  if (!blocking.length) { stopReason = 'converged'; break }
  if (!applied.length) { stopReason = 'stalled'; break }
}

return { stopReason, intentQuestions }
