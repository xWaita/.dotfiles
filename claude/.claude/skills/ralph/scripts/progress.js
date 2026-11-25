export const meta = {
  name: 'ralph-progress',
  description: 'Cut a ralph plan into blocks, draft each block checklist, then review, fix and compact the blocks in parallel until neither the cut nor a checklist changes',
  phases: [
    { title: 'Cut', detail: 'draft PROGRESS.md, or check the block structure against the conventions and fix it' },
    { title: 'Draft', detail: 'per block with no tasks: write its checklist from the PRD and the code' },
    { title: 'Round', detail: 'per block, one agent: check every task and the whole checklist, fix; then compact' },
  ],
}

// args: {prdPath, progressPath, blocksDir: string (absolute), versioned: boolean, draft: boolean,
//        blocks: string[], maxRounds: number, repoHint: string, settings: string}
// The agents' instructions live in ../references/progress/; this script only sequences them and checks what they report.
const { maxRounds = 50, draft = false, versioned = false, blocks: named = [], repoHint = '', settings = '', ...plan } = args
const REFS = '~/.claude/skills/ralph/references/progress'
// A cut and a round can undo each other; this bounds the exchange.
const MAX_CUTS = 5
const FROZEN = ['running', 'done', 'merged']

const obj = properties => ({ type: 'object', properties, required: Object.keys(properties) })
const str = description => ({ type: 'string', description })
const bool = description => ({ type: 'boolean', description })
const int = description => ({ type: 'integer', description })
const list = (items, description) => ({ type: 'array', items, description })
const SEVERITY = { type: 'string', enum: ['Critical', 'High', 'Medium', 'Low'] }
const finding = where => obj({
  key: str(`${where} — the gap, in a few words`),
  severity: SEVERITY,
  fresh: bool('false when the ledger already holds this finding, however reworded'),
  outcome: { type: 'string', enum: ['fixed', 'declined', 'question'] },
  reason: str('why it was declined; empty otherwise'),
})
const QUESTIONS = list(str('file:line — the question, consumers, cost, migration'), 'decisions left for the user, per common/intent-questions.md')

// Every field is required, so an agent that declines the work needs `blocked` to say so instead of inventing values.
const COMMON = {
  shaBefore: str('last commit touching the files you own, read before you changed anything; empty when unversioned'),
  shaAfter: str('the same reading after your last commit; equal to shaBefore when you committed nothing'),
  blocked: bool('true when you did not do the work; the other fields are then empty'),
  note: str('why you stopped when blocked; otherwise empty'),
}
const CUT = obj({
  blocks: list(obj({
    name: str('the block name, as PROGRESS.md and its file name spell it'),
    status: str('its status in PROGRESS.md'),
    tasks: int('top-level tasks in its file, ticked or not'),
    open: int('unticked top-level tasks in its file'),
    changed: bool('true when this pass created the block or changed the tasks in its file'),
  }), 'every block in PROGRESS.md after this pass'),
  findings: list(finding('block or PROGRESS.md:line'), 'every finding on the block structure, each with its outcome; empty on a draft'),
  prdIssues: list(str('PRD.md:line — the defect and what it stops'), 'defects in PRD.md, which this loop does not fix'),
  resolvedIssues: list(str('an entry of planIssues, verbatim'), 'the planIssues entries this pass fixed'),
  intentQuestions: QUESTIONS,
  ...COMMON,
})
const DRAFT = obj({
  tasks: int('top-level tasks written'),
  planIssues: list(str('file:line — the defect and the task it blocks'), 'defects outside your block file'),
  ...COMMON,
})
const ROUND = obj({
  openTasks: int('unticked top-level tasks when you started'),
  findings: list(finding('task id and title, or file:line'), 'every finding, each with its outcome'),
  planIssues: list(str('file:line — the defect and the task it blocks'), 'defects outside your block file: in PRD.md, in PROGRESS.md, or in which block a task sits'),
  intentQuestions: QUESTIONS,
  changes: list(str('what moved, merged, cut or was rewritten, and where'), 'every compaction edit; empty when compaction was skipped'),
  merged: bool('true when compaction merged any tasks'),
  flagged: list(str('file:line — a passage compaction was unsure about and kept'), 'passages left for the user'),
  ...COMMON,
})

const instruct = (file, values) =>
  `Read ${REFS}/${file} and follow it as your instructions.\n\nParameters:\n` +
  Object.entries(values).map(([k, v]) => `- ${k}: ${v}`).join('\n')

// agent() yields null when it dies on an API error after retries.
async function run(file, values, opts) {
  const result = await agent(instruct(file, values), opts)
  if (!result) throw new Error(`${opts.label} failed; the plan files may hold its unfinished work`)
  return result
}

// A step that changed a versioned plan must have committed it, or the next step builds on work the loop never recorded.
const uncommitted = (r, changed) => versioned && changed && r.shaBefore === r.shaAfter

const state = {}            // per block: {stopReason, drafted, ledger, rounds}
const passes = []           // per cut pass: {n, fixed, declined, significant, blocks, sha}
const cutLedger = []
const intentQuestions = []
const planIssues = []
const flagged = []
const addNew = (into, items) => items.forEach(i => { if (!into.includes(i)) into.push(i) })
const base = { ...plan, versioned }
let touched = false         // any draft or round changed a block file since the last cut

// Draft a block that has no tasks, then run rounds on it until one changes nothing that needs another review.
async function refine(b) {
  if (!state[b.name]) state[b.name] = { stopReason: '', drafted: 0, ledger: [], rounds: [] }
  const s = state[b.name]
  const mine = { ...base, block: b.name, blockPath: `${plan.blocksDir}/${b.name}.md` }
  try {
    if (!b.tasks) {
      const d = await run('draft.md', mine, { label: `draft:${b.name}`, phase: 'Draft', schema: DRAFT })
      if (d.blocked) { s.stopReason = `blocked: draft: ${d.note}`; return s }
      if (uncommitted(d, true)) { s.stopReason = `blocked: draft left the block file uncommitted at ${d.shaBefore || 'no commit'}`; return s }
      s.drafted = d.tasks
      touched = true
      addNew(planIssues, d.planIssues)
      log(`${b.name}: drafted ${d.tasks} tasks`)
    }
    if (!maxRounds) { s.stopReason = 'drafted'; return s }
    s.stopReason = 'cap'
    for (let n = 1; n <= maxRounds; n++) {
      const r = await run('round.md', {
        ...mine,
        round: n,
        openQuestions: JSON.stringify(intentQuestions),
        ledger: JSON.stringify(s.ledger),
      }, { label: `round:${b.name}:r${s.rounds.length + 1}`, phase: 'Round', schema: ROUND })
      if (r.blocked) { s.stopReason = `blocked: round ${n}: ${r.note}`; break }
      if (!r.openTasks) { s.stopReason = 'nothing to plan: every task is ticked'; break }
      const fixed = r.findings.filter(f => f.outcome === 'fixed')
      if (uncommitted(r, fixed.length + r.changes.length)) { s.stopReason = `blocked: round ${n} edited the block file but left it uncommitted`; break }
      if (fixed.length + r.changes.length) touched = true
      s.ledger.push(...r.findings.map(({ key, severity, outcome }) => ({ key, severity, outcome })))
      addNew(planIssues, r.planIssues)
      addNew(intentQuestions, r.intentQuestions)
      addNew(flagged, r.flagged)

      const significant = r.findings.filter(f => f.fresh && f.outcome === 'fixed' && f.severity !== 'Low').length
      s.rounds.push({
        fixed: fixed.length,
        declined: r.findings.filter(f => f.outcome === 'declined').map(f => `${f.key}: ${f.reason}`),
        significant,
        compaction: r.changes,
        sha: r.shaAfter,
      })
      log(`${b.name} round ${n}: fixed ${fixed.length}/${r.findings.length}, ${significant} fresh Medium+, ${r.changes.length} compaction edits${r.merged ? ' incl. merges' : ''}`)
      // A merge writes a new task spec, which only a further review checks.
      if (!significant && !r.merged) { s.stopReason = 'converged'; break }
    }
  } catch (e) {
    s.stopReason = `blocked: ${e.message}`
  }
  return s
}

const result = stopReason => ({ stopReason, passes, blocks: state, intentQuestions, planIssues, flagged })
const failed = bs => bs.filter(b => state[b.name].stopReason.startsWith('blocked')).map(b => `${b.name}: ${state[b.name].stopReason}`)

// Named blocks: their rounds only. The cut is left alone.
if (named.length) {
  const bs = named.map(name => ({ name, tasks: 1 }))
  await pipeline(bs, refine)
  const bad = failed(bs)
  if (bad.length) return result(`blocked: ${bad.join('; ')}`)
  return result(bs.some(b => state[b.name].stopReason === 'cap') ? 'cap' : 'converged')
}

for (let pass = 1; pass <= MAX_CUTS; pass++) {
  const drafting = draft && pass === 1
  const cut = await run('cut.md', {
    ...base,
    draft: drafting,
    repoHint,
    settings,
    planIssues: JSON.stringify(planIssues),
    openQuestions: JSON.stringify(intentQuestions),
    ledger: JSON.stringify(cutLedger),
  }, { label: `cut:p${pass}`, phase: 'Cut', schema: CUT })
  if (cut.blocked) return result(`blocked: cut pass ${pass}: ${cut.note}`)
  const fixed = cut.findings.filter(f => f.outcome === 'fixed')
  if (uncommitted(cut, drafting || fixed.length)) return result(`blocked: cut pass ${pass} edited the plan but left it uncommitted`)
  cutLedger.push(...cut.findings.map(({ key, severity, outcome }) => ({ key, severity, outcome })))
  cut.resolvedIssues.forEach(i => { if (planIssues.includes(i)) planIssues.splice(planIssues.indexOf(i), 1) })
  addNew(planIssues, cut.prdIssues)
  addNew(intentQuestions, cut.intentQuestions)

  const significant = cut.findings.filter(f => f.fresh && f.outcome === 'fixed' && f.severity !== 'Low').length
  const live = cut.blocks.filter(b => !FROZEN.includes(b.status))
  // The first pass reviews every open block; later ones only what the cut just changed.
  const targets = live.filter(b => !b.tasks || (pass === 1 ? b.open : b.changed))
  passes.push({
    n: pass,
    fixed: fixed.map(f => `${f.severity} ${f.key}`),
    declined: cut.findings.filter(f => f.outcome === 'declined').map(f => `${f.key}: ${f.reason}`),
    significant,
    blocks: targets.map(b => b.name),
    sha: cut.shaAfter,
  })
  log(`cut pass ${pass}: ${cut.blocks.length} blocks, fixed ${fixed.length}/${cut.findings.length}, ${significant} fresh Medium+; refining ${targets.map(b => b.name).join(', ') || 'nothing'}`)

  touched = false
  await pipeline(targets, refine)
  const bad = failed(targets)
  if (bad.length) return result(`blocked: ${bad.join('; ')}`)
  if (!maxRounds) return result('drafted')
  // Another cut is owed only when something it has not seen changed: its own significant fixes, or a block file.
  if (!significant && !touched) {
    return result(Object.values(state).some(s => s.stopReason === 'cap') ? 'cap' : 'converged')
  }
}

return result('cap')
