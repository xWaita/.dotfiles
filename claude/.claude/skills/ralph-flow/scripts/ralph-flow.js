export const meta = {
  name: 'ralph-flow',
  description: 'Run the ralph loop as a workflow: implement one task, then review and commit it, until the checklist is done',
  phases: [
    { title: 'Implement', detail: 'take the highest-priority unchecked task, write it, format, test' },
    { title: 'Review+commit', detail: 'code-review high, fix every finding, tick the box, commit' },
  ],
}

// args: {prdPath, progressPath, repoDir: string (absolute), maxTasks: number}
// The agents' instructions live in ../references/; this script only sequences them and checks what they report.
const { maxTasks = 100, ...plan } = args
const REFS = '~/.claude/skills/ralph-flow/references'

const obj = properties => ({ type: 'object', properties, required: Object.keys(properties) })
const str = description => ({ type: 'string', description })
const bool = description => ({ type: 'boolean', description })
const int = description => ({ type: 'integer', description })

// Every field is required, so an agent that declines the work needs `blocked` to say so instead of inventing values.
const BLOCKED = {
  blocked: bool('true when you did not do the work; the other fields are then empty or zero'),
  note: str('why you stopped when blocked; otherwise empty'),
}
const IMPLEMENT = obj({
  taskId: str('the checkbox taken, labelled as PROGRESS.md labels it; empty when noneLeft'),
  title: str('one line naming what was built; empty when noneLeft'),
  testCommand: str('the command the task names as its proof, or empty when it names none'),
  noneLeft: bool('true when no unchecked box remained to take; the other fields are then empty'),
  ...BLOCKED,
})
const REVIEW = obj({
  headBefore: str('short HEAD sha read before you changed anything'),
  headAfter: str('short HEAD sha read after committing; equal to headBefore when you did not commit'),
  findingCount: int('findings the review returned'),
  fixedCount: int('findings resolved by an edit'),
  checklistDone: bool('true when no unchecked box remains after this task'),
  ...BLOCKED,
})

const instruct = (file, params) =>
  `Read ${REFS}/${file} and follow it as your instructions.\n\nParameters:\n` +
  Object.entries(params).map(([k, v]) => `- ${k}: ${v}`).join('\n')

// agent() yields null when it dies on an API error after retries; fail the run and leave the tree for the next run.
async function run(file, params, opts, n) {
  const result = await agent(instruct(file, params), opts)
  if (!result) throw new Error(`${opts.label} failed; the tree holds task ${n}'s uncommitted work`)
  return result
}

const tasks = []
let stopReason = 'cap'

for (let n = 1; n <= maxTasks; n++) {
  const impl = await run('implement.md', plan, { label: `implement:t${n}`, phase: 'Implement', schema: IMPLEMENT }, n)
  if (impl.blocked) { stopReason = `blocked: implement on task ${n}: ${impl.note}`; break }
  if (impl.noneLeft) { stopReason = 'complete'; break }
  log(`task ${n}: ${impl.taskId} — ${impl.title}`)

  const { taskId, title, testCommand } = impl
  const done = await run('review.md', { ...plan, taskId, title, testCommand },
    { label: `review+commit:t${n}`, phase: 'Review+commit', schema: REVIEW }, n)
  if (done.blocked) { stopReason = `blocked: review+commit on task ${n}: ${done.note}`; break }
  if (done.headAfter === done.headBefore) {
    stopReason = `blocked: review+commit on task ${n} left HEAD at ${done.headBefore}; the next run resumes it`
    break
  }

  tasks.push({ n, taskId, title, ...done })
  log(`task ${n}: ${done.headAfter} — ${done.fixedCount}/${done.findingCount} findings fixed`)
  if (done.checklistDone) { stopReason = 'complete'; break }
}

return { stopReason, tasks }
