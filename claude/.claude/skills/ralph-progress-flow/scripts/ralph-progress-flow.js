export const meta = {
  name: 'ralph-progress-flow',
  description: 'Draft a missing ralph PROGRESS.md, then each round one agent reviews and fixes it against PRD.md and the code, then compacts it, until a round fixes no fresh Medium+ finding and merges no tasks',
  phases: [
    { title: 'Draft', detail: 'only when PROGRESS.md is missing: write it from PRD.md and the code, commit' },
    { title: 'Review+compact', detail: 'one agent: check every task and the whole checklist, fix, commit; then ai-compact, commit' },
  ],
}

// args: {prdPath, progressPath, repoDir: string (absolute), draft: boolean, maxRounds: number}
// The agents' instructions live in ../references/; this script only sequences them and checks what they report.
const { maxRounds = 50, draft = false, ...plan } = args
const REFS = '~/.claude/skills/ralph-progress-flow/references'

const obj = properties => ({ type: 'object', properties, required: Object.keys(properties) })
const str = description => ({ type: 'string', description })
const bool = description => ({ type: 'boolean', description })
const int = description => ({ type: 'integer', description })
const list = (items, description) => ({ type: 'array', items, description })
const SEVERITY = { type: 'string', enum: ['Critical', 'High', 'Medium', 'Low'] }

// Every field is required, so an agent that declines the work needs `blocked` to say so instead of inventing values.
const COMMON = {
  headBefore: str('short HEAD sha read before you changed anything'),
  headAfter: str('short HEAD sha after your last commit; equal to headBefore when you committed nothing'),
  blocked: bool('true when you did not do the work; the other fields are then empty'),
  note: str('why you stopped when blocked; otherwise empty'),
}
const DRAFT = obj({ tasks: int('top-level tasks written'), ...COMMON })
const ROUND = obj({
  openTasks: int('unticked top-level tasks when you started'),
  findings: list(obj({
    key: str('task number and title, or PROGRESS.md:line — the gap, in a few words'),
    severity: SEVERITY,
    fresh: bool('false when the ledger already holds this finding, however reworded'),
    outcome: { type: 'string', enum: ['fixed', 'declined', 'question'] },
    reason: str('why it was declined; empty otherwise'),
  }), 'every finding, each with its outcome'),
  prdIssues: list(str('PRD.md:line — the defect and the task it blocks'), 'defects in PRD.md, which this loop does not fix'),
  intentQuestions: list(str('file:line — the question, consumers, cost, migration'), 'decisions left for the user, per common/intent-questions.md'),
  changes: list(str('what moved, merged, cut or was rewritten, and where'), 'every compaction edit; empty when compaction was skipped'),
  merged: bool('true when compaction merged any tasks'),
  flagged: list(str('PROGRESS.md:line — a passage compaction was unsure about and kept'), 'passages left for the user'),
  ...COMMON,
})

const instruct = (file, params) =>
  `Read ${REFS}/${file} and follow it as your instructions.\n\nParameters:\n` +
  Object.entries(params).map(([k, v]) => `- ${k}: ${v}`).join('\n')

// agent() yields null when it dies on an API error after retries; fail the run and leave the tree for the next run.
async function run(file, params, opts) {
  const result = await agent(instruct(file, params), opts)
  if (!result) throw new Error(`${opts.label} failed; the plan files may hold its uncommitted work`)
  return result
}

// A step that changed the plan must have committed it, or the next step builds on work the loop never recorded.
const uncommitted = (before, after, changed) => changed && before === after

const ledger = []           // every review finding seen: {key, severity, outcome}
const intentQuestions = []
const prdIssues = []
const flagged = []
const rounds = []
const addNew = (into, items) => items.forEach(i => { if (!into.includes(i)) into.push(i) })
let stopReason = 'cap'

if (draft) {
  const d = await run('draft.md', plan, { label: 'draft', phase: 'Draft', schema: DRAFT })
  if (d.blocked) return { stopReason: `blocked: draft: ${d.note}`, rounds, intentQuestions, prdIssues, flagged }
  if (uncommitted(d.headBefore, d.headAfter, true)) return { stopReason: `blocked: draft left HEAD at ${d.headBefore}`, rounds, intentQuestions, prdIssues, flagged }
  log(`draft: ${d.tasks} tasks (${d.headAfter})`)
}

for (let n = 1; n <= maxRounds; n++) {
  const r = await run('review.md', {
    ...plan,
    round: n,
    openQuestions: JSON.stringify(intentQuestions),
    ledger: JSON.stringify(ledger),
  }, { label: `round:r${n}`, phase: 'Review+compact', schema: ROUND })
  if (r.blocked) { stopReason = `blocked: round ${n}: ${r.note}`; break }
  if (!r.openTasks) { stopReason = 'nothing to plan: every task is ticked'; break }
  const fixed = r.findings.filter(f => f.outcome === 'fixed')
  if (uncommitted(r.headBefore, r.headAfter, fixed.length + r.changes.length)) { stopReason = `blocked: round ${n} edited the plan but left HEAD at ${r.headBefore}`; break }
  ledger.push(...r.findings.map(({ key, severity, outcome }) => ({ key, severity, outcome })))
  addNew(prdIssues, r.prdIssues)
  addNew(intentQuestions, r.intentQuestions)
  addNew(flagged, r.flagged)

  const significant = r.findings.filter(f => f.fresh && f.outcome === 'fixed' && f.severity !== 'Low').length
  rounds.push({
    n,
    fixed: fixed.length,
    declined: r.findings.filter(f => f.outcome === 'declined').map(f => `${f.key}: ${f.reason}`),
    significant,
    compaction: r.changes,
    sha: r.headAfter,
  })
  log(`round ${n}: fixed ${fixed.length}/${r.findings.length}, ${significant} fresh Medium+, ${r.changes.length} compaction edits${r.merged ? ' incl. merges' : ''} (${r.headAfter})`)
  // A merge writes a new task spec, which only a further review checks.
  if (!significant && !r.merged) { stopReason = 'converged'; break }
}

return { stopReason, rounds, intentQuestions, prdIssues, flagged }
