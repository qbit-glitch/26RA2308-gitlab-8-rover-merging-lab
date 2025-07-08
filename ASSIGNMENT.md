# Git Lab Assignment: Kestrel-1 Rover, Merge Day

**Course:** 26RA2308 Git for Software Development and Collaboration
**Builds on:** Experiments 1 to 7. **Based on:** Experiment 8 (Merging Branches and Resolving Conflicts)
**Time allowed:** 1 hour. **Marks:** 100

---

## The story

It is 14:00 on Friday at the Kestrel-1 rover lab. Release `v0.2` goes out at 15:00 and you are the release
manager. **Asha**, **Ben** and **Chitra** have each finished a branch, and all three are waiting on the
shared copy of the project. The lab has one rule:

> **`main` receives work only by merge, one branch at a time.**

In the next hour you bring the three branches home: one slides in without a fuss, one needs a real merge
commit, and one collides with another and has to be settled by hand. Every command is a command from
Experiment 8: `git merge`, `git merge -m`, `git cat-file`, `git status` during a merge, conflict markers,
`git add` and `git commit` to finish a merge, `git branch -r --merged` and `git log --merges`. Along the way you
reuse `git config` and aliases (Experiment 3), `git commit` (Experiments 4 and 5), `git log` and `git status`
(Experiment 6), branches (Experiment 7) and the terminal skills from Experiments 1 and 2.

## What you need

`git`, `python3` and `nano`. Check with `git --version && python3 --version`. If your terminal does not print
English messages, run `export LC_ALL=C` first, because the grader reads what Git prints. If a long output
opens in a pager (a screen with `:` or `(END)` at the bottom), press `q` to leave it.

## How to edit a file with nano

You edit one file in this lab (Task 4), and only with `nano`. Never use `echo` to write into a file.

1. `nano <file>` opens the file. The cursor starts at the **top** of the file.
2. Type exactly the text shown, pressing `Enter` where the text shows a new line.
3. Keys that act on whole lines: `Ctrl+K` **cuts the line the cursor is on** (the next line moves up under the
   cursor) and `↓` moves the cursor down one line.
4. Save with `Ctrl+O` and then `Enter` (that confirms the file name). Leave with `Ctrl+X`.

If nano says "Save modified buffer?", press `Y` and then `Enter`. If you made a mistake before saving, press
`Ctrl+X`, then `N`, and start again. Wherever the text shows `Your Full Name`, type your own name, exactly as in
`git config user.name`.

## Rules

1. Work **only inside your own clone**, on branch `main`, for the whole lab. Do not push anything.
2. Do not use `git rebase`, `git reset` or `git cherry-pick`. Do not create branches. The teammates' work is
   merged straight from the shared copy: its names start with `origin/`.
3. Type the commands yourself. The grader checks that your pasted output matches what is really in your
   repository, so output copied from a classmate is detected.
4. Keep the commit messages exactly as written.

## How you hand in your work

1. In Task 1 you copy `submission/outputs.template.txt` to `submission/outputs.txt`.
2. After **each step** (numbered **1.1**, **1.2**, ...), paste what the terminal printed under the matching
   `--- N.M` line of `submission/outputs.txt`, replacing `(paste output here)`. Do not edit or delete the
   `=== TASK` and `--- N.M` lines. Type your answers after the colon of the `ANSWER-n :` lines (the line just
   below each `# Qn` question). Any editor is fine for `submission/outputs.txt`.
3. Fill in your name and registration number at the top of the file.
4. Run the automatic grader whenever you want to see where you stand:

   ```bash
   python3 tests/grade.py
   ```

   It prints **PASS** or **FAIL** for every task, tells you exactly which check failed, and shows your score out
   of 100. You can fix a mistake and run it again as often as you like.
5. When you are done, show the final grader output to your instructor (it is also saved in
   `submission/results.txt`), and submit `submission/outputs.txt` as instructed.

## Time plan

| Task | Time on the clock | Topic | Suggested time | Marks |
|---|---|---|---|---|
| 1 | 14:00 | Take over the release board | 7 min | 10 |
| 2 | 14:08 | Fast-forward | 7 min | 15 |
| 3 | 14:15 | A real merge | 9 min | 20 |
| 4 | 14:25 | A merge conflict | 15 min | 40 |
| 5 | 14:40 | Wrap up | 5 min | 15 |
| | | Buffer for running the grader and fixing mistakes | 17 min | |

**Skipped a task, or running behind?** You do not lose the rest of the lab. Each merge builds on the one before
it, so a task needs the work of the task before: Task 3 needs `main` to have moved (Task 2), Task 4 needs the
first merge commit (Task 3) and Task 5 needs the second one (Task 4). If you skipped one, the **catch-up box**
at the start of the next task brings `main` to the state you need, in one to four lines. If you skipped
several, run their boxes in order. You lose only the marks of the task you skipped.

---

## Task 1: Take over the release board (10 marks)

Get your own copy of the project, tell Git who you are, and look at what is waiting before you merge anything.

```bash
git clone https://github.com/qbit-glitch/26RA2308-gitlab-8-rover-merging-lab.git \
    rover-merging-lab
cd rover-merging-lab
cp submission/outputs.template.txt submission/outputs.txt
git config user.name "Your Full Name"
git config user.email "your.email@example.com"
git config alias.tree "log --oneline --graph --decorate --all"
git config merge.ff true
git config merge.conflictstyle merge
```

Use your own real name and e-mail (not the placeholders above, and not one of the teammates'). Do **not** use
`--global` here. The last two lines make sure that settings on your machine cannot change what Git prints in
this lab. Your instructor may give you a different clone URL.

* **1.1** Run `git config --local --list` and paste the output.
* **1.2** Run `git branch -a` and paste the output. You have only `main`, but the shared copy holds the three
  branches under `remotes/origin/`. Those are the names you will merge.
* **1.3** Run `git tree` (your alias) and paste the output. All three branches start at the same commit as
  `main` and hold one commit each.
* Then type your answer to `ANSWER-1` in the file (there is no pasted output for it): how many feature branches
  are waiting to be merged?

## Task 2: Fast-forward (15 marks)

Start with Asha's branch, `origin/feature/turn-left`. Preview it, then merge it. Nobody has added anything to
`main` since her branch began, so Git has nothing to combine: it only has to move `main` forward.

*Needs:* only the setup of Task 1.

```bash
git log --oneline main..origin/feature/turn-left
```

* **2.1** Paste the output. `main..X` means "commits that `X` has and `main` does not".

```bash
git merge origin/feature/turn-left
```

* **2.2** Paste the output. Read the word `Fast-forward`: no new commit was made, `main` just slid forward.

```bash
git tree
```

* **2.3** Paste the output. `main` and Asha's branch now name the same commit, and `origin/main` stayed behind.

## Task 3: A real merge (20 marks)

Now Ben's branch, `origin/feature/fast-loop`. It also began at the old tip, but `main` has moved since (Asha's
commit), so the two lines of work have to be joined by a new commit with **two parents**. A merge commit needs
a message, and `-m` supplies it.

*Needs:* Asha's branch merged into `main` (Task 2).

> **Catch-up box: only if you skipped Task 2.** Run this one line, once, on `main`. It does what Task 2
> does. If you did Task 2, do **not** run it. There is nothing to paste for it, and you lose only the marks of
> Task 2.
>
> ```bash
> git merge origin/feature/turn-left
> ```

```bash
git merge origin/feature/fast-loop -m "merge: bring in fast sensor loop"
```

* **3.1** Paste the output. It says `Merge made by the 'ort' strategy.` (an older Git says `'recursive'`).

```bash
git tree
```

* **3.2** Paste the output. The history forks and joins again: look for the `|\` line.

```bash
git cat-file -p HEAD
```

* **3.3** Paste the output. It is the raw commit. A normal commit has one `parent` line, a merge commit has two:
  the first is where `main` was (Asha's commit), the second is the tip of Ben's branch. Type the **second**
  `parent` number as `ANSWER-2` in the file.

## Task 4: A merge conflict (40 marks)

Chitra's branch, `origin/fix/echo-timeout`, changes the same line of `src/sensor_limits.h` that Ben changed:
Ben made the echo timeout 40 ms, Chitra wants 30 ms. Git cannot choose between two edits of one line, so it
stops and asks you.

*Needs:* the merge commit from Task 3.

> **Catch-up box: only if you skipped Task 3.** Run this one line, once, on `main`. It does what Task 3
> does. If you did Task 3, do **not** run it. There is nothing to paste for it, and you lose only the marks of
> Task 3. (If you skipped Task 2 as well, run its box first.)
>
> ```bash
> git merge origin/feature/fast-loop -m "merge: bring in fast sensor loop"
> ```

```bash
git merge origin/fix/echo-timeout
```

* **4.1** Paste the output. It is **supposed to stop** with `CONFLICT` and `Automatic merge failed`. The merge is
  now half done.

```bash
git status
```

* **4.2** Paste the output. Find `You have unmerged paths` and `both modified`.

```bash
cat src/sensor_limits.h
```

* **4.3** Paste the output. Git wrote both versions into the file, between markers:

  ```text
  <<<<<<< HEAD                     <- the line on main (Ben's, 40)
  #define SENSOR_TIMEOUT_MS 40
  =======
  #define SENSOR_TIMEOUT_MS 30     <- the line on Chitra's branch
  >>>>>>> origin/fix/echo-timeout
  ```

Both numbers pass the team's limits check. The team decides to keep **Chitra's 30**, because her camera timing
needs it. Resolve the file in nano:

```bash
nano src/sensor_limits.h
```

Type this one line and press `Enter` after it (the cursor is now at the start of the `<<<<<<<` line):

```text
/* resolved by Your Full Name */
```

Then press `Ctrl+K` **three times** (this cuts `<<<<<<< HEAD`, Ben's line and `=======`), press `↓` **once**
(the cursor is now on Chitra's line, so this moves it down to the `>>>>>>>` line) and press `Ctrl+K` **once**
more. The file must now be exactly these four lines. Save and exit.

```text
/* resolved by Your Full Name */
#define SENSOR_TIMEOUT_MS 30
#define SENSOR_MAX_CM 400
#define SENSOR_MIN_CM 2
```

```bash
python3 tests/check_limits.py
```

* **4.4** Paste the output. It must end with `ALL CHECKS PASSED`.

`git add` tells Git "this file is settled", and `git commit` finishes the merge:

```bash
git add src/sensor_limits.h
git commit -m "merge: settle echo timeout at 30 ms"
```

* **4.5** Paste the output of the `git commit` command.

```bash
git tree
```

* **4.6** Paste the output. Both branches are now part of `main`.

## Task 5: Wrap up (15 marks)

Check what the merges achieved before the 15:00 release. You should still be on `main`.

*Needs:* both merge commits, from Tasks 3 and 4.

> **Catch-up box: only if you skipped Task 4.** Run these four lines, once, on `main`. They start the merge
> that Task 4 teaches, and settle the conflict the quick way: they take Chitra's whole file as it is, without
> nano. If you did Task 4, do **not** run them. There is nothing to paste for them, and you lose only the marks of
> Task 4. (If you skipped Task 2 or 3 as well, run their boxes first.)
>
> ```bash
> git merge origin/fix/echo-timeout
> git checkout --theirs src/sensor_limits.h
> git add src/sensor_limits.h
> git commit -m "merge: settle echo timeout at 30 ms"
> ```

```bash
git branch -r --merged
```

* **5.1** Paste the output (remote branches whose work is already in the branch you are on).

```bash
git log --oneline --merges
```

* **5.2** Paste the output. Only your two merge commits are listed: the fast-forward made none.

```bash
git status
```

* **5.3** Paste the output. `main` is ahead of the shared copy, and the working tree must be clean.
* Then type your answer to `ANSWER-3` in the file: by how many commits is `main` now ahead of `origin/main`?

## Finish

```bash
python3 tests/grade.py
```

You want to see `PASS` for all five tasks and `TOTAL: 100/100`. Anything marked `FAIL` is listed with the reason;
fix it and run the grader again.

## Marks

| Task | Marks | How it is checked |
|---|---|---|
| 1 | 10 | your pasted config matches the repository's real configuration; the branch listings and the graph show the three branches |
| 2 | 15 | the preview, `Fast-forward` and the graph are right; `main` really moved to Asha's own commit and the reflog says so |
| 3 | 20 | a merge commit with the right two parents and both changes; the raw commit is pasted; one answer |
| 4 | 40 | the conflict, the status and the markers are pasted; the resolved file has no markers, keeps 30, carries your name and passes the limits check; the second merge commit has the right parents |
| 5 | 15 | the merged branches, the two merge commits and `ahead by 5`; the working tree is clean; one answer |

A task shows **PASS** only when every check in it passes, and you earn marks for each check that passes even if
the task as a whole fails.

## If something goes wrong

* **You skipped a task and a later one fails.** Run the catch-up box at the start of the task after the one you
  skipped (in order, if you skipped several), then carry on.
* **An editor opened and asked for a commit message.** You left out `-m "..."`. Save and exit (nano: `Ctrl+O`,
  `Enter`, `Ctrl+X`; vim: `Esc`, then `:wq` and `Enter`). Then fix the message with
  `git commit --amend -m "<the message from the step>"`.
* **The merge went wrong and you want to start it again.** While a merge is in progress, `git merge --abort`
  puts everything back as it was before that merge. Then run the merge command again.
* **You saved the wrong text in nano.** Run `git checkout --merge src/sensor_limits.h`: it rewrites the file
  with the conflict markers, so you can edit it again.
* **`python3 tests/check_limits.py` prints `FAIL`.** Read the `FAIL` lines: a marker line left in the file or two
  `SENSOR_TIMEOUT_MS` lines mean the nano step was not finished. Open the file again and remove them.
* **`error: Your local changes would be overwritten by merge`.** A file was changed before the merge. Look at
  `git status`; undo the change with `git restore <file>` and merge again.
* **`git commit` says `Committing is not possible because you have unmerged files`.** You forgot
  `git add src/sensor_limits.h`. Run it, then commit again.
* **You merged in the wrong order.** Delete the folder, clone again and redo the tasks (your pasted outputs must
  be produced in the new clone).
* **`tests/grade.py` says it cannot find `origin/main`.** You are not inside your clone: `cd rover-merging-lab`.
