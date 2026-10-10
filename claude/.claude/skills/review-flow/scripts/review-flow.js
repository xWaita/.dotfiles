export const meta = {
  name: 'review-flow',
  description: 'Refactor then code-review a target, committing each, until code-review finds nothing significant',
  phases: [
    { title: 'Refactor', detail: 'apply Medium+ refactors around the target, commit' },
    { title: 'Review', detail: 'code-review high, fix real findings, commit, decide whether to continue' },
  ],
}

// args: {target: string, repoDir: string (absolute), maxRounds: number}
// The agents' instructions live in ../references/; this script only sequences them and checks what they report.
const { maxRounds = 5, target, repoDir } = args
const REFS = '~/.claude/skills/review-flow/references'

const obj = properties => ({ type: 'object', properties, required: Object.keys(properties) })
const str = description => ({ type: 'string', description })
const bool = description => ({ type: 'boolean', description })
const list = (items, description) => ({ type: 'array', items, description })
const SEVERITY = { type: 'string', enum: ['Critical', 'High', 'Medium', 'Low'] }

// Every field is required, so an agent that declines the work needs `blocked` to say so instead of inventing values.
const COMMON = {
  headBefore: str('short HEAD sha read before you changed anything'),
  headAfter: str('short HEAD sha read after committing; equal to headBefore when you did not commit'),
  blocked: bool('true when you did not do the work; the other fields are then empty'),
  note: str('why you stopped when blocked; otherwise empty'),
}
const REFACTOR = obj({
  findings: list(obj({
    key: str('file:symbol — the smell, in a few words'),
    severity: SEVERITY,
    applied: bool('true when you applied it'),
  }), 'every rated finding, applied or not'),
  intentQuestions: list(str('file:line — keep <capability>? consumers, cost'), 'capability removals left for the user'),
  ...COMMON,
})
const REVIEW = obj({
  findings: list(obj({
    key: str('file:symbol — the defect, in a few words'),
    severity: SEVERITY,
    fresh: bool('false when the ledger already holds this finding, however reworded'),
    outcome: { type: 'string', enum: ['fixed', 'declined'] },
    reason: str('why it was declined; empty when fixed'),
  }), 'every finding code-review returned'),
  continue: bool('true when any fresh finding rated Medium or above was fixed'),
  ...COMMON,
})

const instruct = (file, params) =>
  `Read ${REFS}/${file} and follow it as your instructions.\n\nParameters:\n` +
  Object.entries(params).map(([k, v]) => `- ${k}: ${v}`).join('\n')

// agent() yields null when it dies on an API error after retries; fail the run and leave the tree for the next run.
async function run(file, params, opts) {
  const result = await agent(instruct(file, params), opts)
  if (!result) throw new Error(`${opts.label} failed; the tree may hold its uncommitted work`)
  return result
}

const ledger = []        // every review finding seen: {key, severity, outcome}
const applied = []       // every refactor applied: key
const rounds = []
const intentQuestions = []
let stopReason = 'cap'

for (let n = 1; n <= maxRounds; n++) {
  const ref = await run('refactor.md',
    { target, repoDir, appliedRefactors: JSON.stringify(applied) },
    { label: `refactor:r${n}`, phase: 'Refactor', schema: REFACTOR })
  if (ref.blocked) { stopReason = `blocked: refactor in round ${n}: ${ref.note}`; break }
  const refApplied = ref.findings.filter(f => f.applied)
  if (refApplied.length && ref.headAfter === ref.headBefore) {
    stopReason = `blocked: refactor in round ${n} applied changes but left HEAD at ${ref.headBefore}`
    break
  }
  applied.push(...refApplied.map(f => f.key))
  intentQuestions.push(...ref.intentQuestions)
  log(`round ${n}: ${refApplied.length} refactors applied${refApplied.length ? ` (${ref.headAfter})` : ''}`)

  const rev = await run('review.md',
    { target, repoDir, ledger: JSON.stringify(ledger) },
    { label: `review:r${n}`, phase: 'Review', schema: REVIEW })
  if (rev.blocked) { stopReason = `blocked: review in round ${n}: ${rev.note}`; break }
  const fixed = rev.findings.filter(f => f.outcome === 'fixed')
  if (fixed.length && rev.headAfter === rev.headBefore) {
    stopReason = `blocked: review in round ${n} fixed findings but left HEAD at ${rev.headBefore}`
    break
  }
  ledger.push(...rev.findings.map(({ key, severity, outcome }) => ({ key, severity, outcome })))

  const significant = rev.findings.filter(f => f.fresh && f.outcome === 'fixed' && f.severity !== 'Low').length
  rounds.push({
    n,
    refactor: { applied: refApplied.map(f => `${f.severity} ${f.key}`), sha: ref.headAfter },
    review: { fixed: fixed.length, declined: rev.findings.length - fixed.length, significant, sha: rev.headAfter },
    belowFloor: ref.findings.filter(f => !f.applied).map(f => `${f.severity} ${f.key}`),
  })
  log(`round ${n}: review fixed ${fixed.length}/${rev.findings.length}, ${significant} fresh Medium+ (${rev.headAfter})`)
  if (!rev.continue) { stopReason = 'converged'; break }
}

return { stopReason, rounds, intentQuestions }
