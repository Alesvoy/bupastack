# Engineer report format

Send the report to the coordinator thread with `t3_thread_send`, as plain text, one field per line, in this order.

```
Engineer <slug>: PR ready
PR: <URL> (head <short sha>)
What changed:
- <One to three plain bullets, for the people who use the change.>
Verified: <repo checks and tests, and the result>. <verify journeys, and the result>. QA <passed> of <total> scenarios pass (evidence <evidence folder>).
CI: <each check's result on the head commit. With no CI, the repo's checks you ran on it, and the result.>
Review: sol-loop, <rounds> rounds, <model> approved <short sha>. Fixed <findings>. Declined <findings, each with its reason>.
Departures: <each difference from the ticket, or "none">.
Not verified: <what the evidence doesn't cover, or "nothing">.
```

When `sol-loop` ended stuck, write that `<model>` didn't approve in the Review line, and give both sides of each disputed finding.

When you can't finish, such as when QA or CI won't pass, send a blocked report instead:

```
Engineer <slug>: blocked
PR: <URL> (draft, head <short sha>)
Blocker: <what stopped you>
Needs: <what would unblock it, such as a decision the ticket doesn't make>
```

Add any line from the ready report that helps the coordinator decide.
