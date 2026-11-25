export const meta = {
  name: 'ralph-run',
  description: 'Run one ralph block: implement one task, then review and commit it, until the block checklist is done',
  phases: [
    { title: 'Implement', detail: 'take the highest-priority unchecked task of the block, write it, format, test' },
    { title: 'Review+commit', detail: 'code-review each changed worktree, fix every finding, tick the box, commit' },
  ],
}

// args: {prdPath, progressPath, blockPath: string (absolute), worktrees: [{repo, path}], review: string, maxTasks: number}
// The agents' instructions live in ../references/run/; this script only sequences them and checks what they report.
const { maxTasks = 100, review = 'high', worktrees, ...plan } = args
const REFS = '~/.claude/skills/ralph/references/run'
const block = plan.blockPath.split('/').pop().replace(/\.md$/, '')
const params = { ...plan, worktrees: worktrees.map(w => `${w.repo}=${w.path}`).join(' ') }

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
  taskId: str('the checkbox taken, labelled as the block file labels it; empty when noneLeft'),
  title: str('one line naming what was built; empty when noneLeft'),
  testCommand: str('the command the task names as its proof, with its repo prefix, or empty when it names none'),
  noneLeft: bool('true when no unchecked box remained to take; the other fields are then empty'),
  ...BLOCKED,
})
// One string covers every worktree, so a commit in any of them changes it.
const REVIEW = obj({
  headBefore: str('short HEAD of every worktree as `repo=sha` joined by spaces, read before you changed anything'),
  headAfter: str('the same reading after committing; equal to headBefore when you did not commit'),
  findingCount: int('findings the reviews returned, over every changed worktree'),
  fixedCount: int('findings resolved by an edit'),
  checklistDone: bool('true when no unchecked box remains in the block after this task'),
  ...BLOCKED,
})

const instruct = (file, values) =>
  `Read ${REFS}/${file} and follow it as your instructions. Invoke the code-review skill only where they say to and with the arguments they give, never while activating skills.\n\nParameters:\n` +
  Object.entries(values).map(([k, v]) => `- ${k}: ${v}`).join('\n')

// agent() yields null when it dies on an API error after retries; fail the run and leave the trees for the next run.
async function run(file, values, opts, n) {
  const result = await agent(instruct(file, values), opts)
  if (!result) throw new Error(`${opts.label} failed; the worktrees hold task ${n}'s uncommitted work`)
  return result
}

const tasks = []
let stopReason = 'cap'

for (let n = 1; n <= maxTasks; n++) {
  const impl = await run('implement.md', params, { label: `${block}:implement:t${n}`, phase: 'Implement', schema: IMPLEMENT }, n)
  if (impl.blocked) { stopReason = `blocked: implement on task ${n}: ${impl.note}`; break }
  if (impl.noneLeft) { stopReason = 'complete'; break }
  log(`${block} task ${n}: ${impl.taskId} — ${impl.title}`)

  const { taskId, title, testCommand } = impl
  const done = await run('review-commit.md', { ...params, review, taskId, title, testCommand },
    { label: `${block}:review+commit:t${n}`, phase: 'Review+commit', schema: REVIEW }, n)
  if (done.blocked) { stopReason = `blocked: review+commit on task ${n}: ${done.note}`; break }
  if (done.headAfter === done.headBefore) {
    stopReason = `blocked: review+commit on task ${n} left HEAD at ${done.headBefore}; the next run resumes it`
    break
  }

  tasks.push({ n, taskId, title, ...done })
  log(`${block} task ${n}: ${done.headAfter} — ${done.fixedCount}/${done.findingCount} findings fixed`)
  if (done.checklistDone) { stopReason = 'complete'; break }
}

return { stopReason, block, tasks }
