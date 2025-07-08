"""Graders for the five tasks of the Merging lab."""
from __future__ import annotations

import re
from typing import Optional

from .context import Ctx
from .facts import (
    FAST_BRANCH, FEATURE_BRANCHES, FIX_BRANCH, LIMITS_PATH, MERGE1_SUBJECT, MERGE2_SUBJECT, TURN_BRANCH,
    TURN_SUBJECT, limits_problems,
)
from .framework import Task
from .textutil import (
    branch_names, decorations, get_answer_int, get_answer_sha, oneline_entries, parse_branch_list,
    parse_config_list, parse_status, sha_matches, strip_decoration,
)

PLACEHOLDER_NAMES = {"", "your full name", "your name"}
PLACEHOLDER_EMAILS = {"", "your.email@example.com"}
MERGE_MADE_RE = re.compile(r"Merge made by the '(?:ort|recursive)' strategy\.")
GRAPH_NODE_RE = re.compile(r"(?m)^[ |\\/]*\*")
FORK_RE = re.compile(r"(?m)^\|\\")
TIMEOUT_40 = "#define SENSOR_TIMEOUT_MS 40"
TIMEOUT_30 = "#define SENSOR_TIMEOUT_MS 30"


def _line_with(text: str, *needles: str) -> bool:
    """True when one line of the text holds every needle."""
    return any(all(n in line for n in needles) for line in text.split("\n"))


def _remote(branch: str) -> str:
    return f"origin/{branch}"


# -- Task 1 -----------------------------------------------------------------
def grade_task1(ctx: Ctx) -> Task:
    """Task 1: set up, then read the board (branch -a, the graph)."""
    t = Task(1, "Take over the release board", 10, ctx.repo_mode)
    f = ctx.facts
    cfg = parse_config_list(ctx.step("1.1"))
    name, email = cfg.get("user.name", ""), cfg.get("user.email", "")
    t.check(2, "1.1 user.name and user.email are your own details (not the placeholders)",
            lambda: name.lower() not in PLACEHOLDER_NAMES and "@" in email and email.lower() not in PLACEHOLDER_EMAILS)
    t.check(1, "1.1 alias.tree is set to 'log --oneline --graph --decorate --all'",
            lambda: cfg.get("alias.tree") == "log --oneline --graph --decorate --all")
    rows = parse_branch_list(ctx.step("1.2"))
    names = {r.name for r in rows}
    wanted = {"remotes/origin/main"} | {f"remotes/origin/{b}" for b in FEATURE_BRANCHES}
    t.check(2, "1.2 branch -a lists main (checked out) and the remote branches of the three feature branches",
            lambda: wanted <= names and any(r.current and r.name == "main" for r in rows))
    s13 = ctx.step("1.3")
    t.check(2, "1.3 is a graph (git tree) that shows main, origin/main and the three feature branches",
            lambda: ({"main", "origin/main"} | {_remote(b) for b in FEATURE_BRANCHES}) <= decorations(s13)
            and GRAPH_NODE_RE.search(s13) is not None)
    t.check(1, "ANSWER-1 is 3 (the three feature branches waiting to be merged)",
            lambda: get_answer_int(ctx.text, 1) == "3")
    t.check(2, "live repo: the pasted identity is the one configured in this clone and is not a teammate's",
            lambda: bool(name) and name == f.config_value("user.name") and email == f.config_value("user.email")
            and name.lower() not in f.published_names() and email.lower() not in f.published_emails(),
            needs_repo=True)
    return t


# -- Task 2 -----------------------------------------------------------------
def grade_task2(ctx: Ctx) -> Task:
    """Task 2: preview a branch, then merge it by fast-forward."""
    t = Task(2, "Fast-forward", 15, ctx.repo_mode)
    f = ctx.facts
    turn = f.tips[TURN_BRANCH]
    entries = oneline_entries(ctx.step("2.1"))
    t.check(2, "2.1 main..origin/feature/turn-left lists exactly the one commit 'feat(control): add left turn routine'",
            lambda: len(entries) == 1 and entries[0].subject.endswith(TURN_SUBJECT) and sha_matches(entries[0].sha, turn))
    s22 = ctx.step("2.2")
    t.check(2, "2.2 merge output says Fast-forward", lambda: "Fast-forward" in s22)
    updating = re.search(r"Updating ([0-9a-f]{7,40})\.\.([0-9a-f]{7,40})", s22)
    t.check(1, "2.2 'Updating <old>..<new>' ends at the tip of origin/feature/turn-left and starts at origin/main",
            lambda: updating is not None and sha_matches(updating.group(2), turn)
            and sha_matches(updating.group(1), f.origin_tip))
    t.check(1, "2.2 lists src/controller.c and src/controller.h", lambda: "src/controller.c" in s22 and "src/controller.h" in s22)
    s23 = ctx.step("2.3")
    t.check(2, "2.3 graph: main (HEAD) and origin/feature/turn-left sit on the same commit",
            lambda: _line_with(s23, "HEAD -> main", "origin/feature/turn-left"))
    t.check(1, "2.3 origin/main is left behind, on an older commit than main",
            lambda: _line_with(s23, "origin/main") and not _line_with(s23, "HEAD -> main", "origin/main"))
    chain = f.first_parent_chain() if ctx.repo_mode else []
    t.check(3, "live repo: the first thing main gained is the published commit of feature/turn-left itself "
               "(a fast-forward moved main; no merge commit was made for it)",
            lambda: bool(chain) and chain[0] == turn, needs_repo=True,
            why=lambda: "main's first new commit is not the turn-left commit (did you use --no-ff or copy the code by hand?)")
    t.check(3, "live repo: HEAD's reflog records 'merge origin/feature/turn-left: Fast-forward'",
            lambda: "merge origin/feature/turn-left: Fast-forward" in f.head_reflog(), needs_repo=True)
    return t


# -- Task 3 -----------------------------------------------------------------
def _second_parent(text: str) -> Optional[str]:
    parents = re.findall(r"(?m)^parent ([0-9a-f]{40})$", text)
    return parents[1] if len(parents) == 2 else None


def grade_task3(ctx: Ctx) -> Task:
    """Task 3: a true merge (two parents)."""
    t = Task(3, "A real merge", 20, ctx.repo_mode)
    f = ctx.facts
    turn, fast = f.tips[TURN_BRANCH], f.tips[FAST_BRANCH]
    s31 = ctx.step("3.1")
    t.check(3, "3.1 merge output: Merge made by the 'ort' (or 'recursive') strategy.", lambda: MERGE_MADE_RE.search(s31) is not None)
    t.check(1, "3.1 changes only src/sensor_limits.h (1 file changed)",
            lambda: "src/sensor_limits.h" in s31 and re.search(r"\b1 file changed", s31) is not None)
    s32 = ctx.step("3.2")
    t.check(1, "3.2 the graph forks and joins (a '|\\' line)", lambda: FORK_RE.search(s32) is not None)
    t.check(2, "3.2 the merge commit 'merge: bring in fast sensor loop' is at HEAD -> main",
            lambda: _line_with(s32, "HEAD -> main", MERGE1_SUBJECT))
    s33 = ctx.step("3.3")
    parents = re.findall(r"(?m)^parent ([0-9a-f]{40})$", s33)
    author = re.search(r"(?m)^author (.+) <([^>]*)> \d+ [+-]\d{4}$", s33)
    cfg = parse_config_list(ctx.step("1.1"))
    t.check(2, "3.3 cat-file shows a tree line and exactly two parent lines", lambda: "tree " in s33 and len(parents) == 2)
    t.check(2, "3.3 the first parent is the tip of feature/turn-left (where main was) and the second is the tip of "
               "feature/fast-loop",
            lambda: len(parents) == 2 and parents[0] == turn and parents[1] == fast)
    t.check(1, "3.3 the author line is you (the name and e-mail of your own configuration, not a teammate's)",
            lambda: author is not None and author.group(1).lower() not in f.published_names()
            and author.group(2).lower() not in f.published_emails()
            and (not cfg.get("user.name") or author.group(1) == cfg["user.name"]))
    t.check(1, "3.3 the commit message is 'merge: bring in fast sensor loop'", lambda: MERGE1_SUBJECT in s33)
    t.check(2, "ANSWER-2 is the second parent of the merge commit (the tip of feature/fast-loop)",
            lambda: sha_matches(get_answer_sha(ctx.text, 2), fast))
    merge1 = f.merge_commit(MERGE1_SUBJECT) if ctx.repo_mode else None
    t.check(3, "live repo: main has the merge commit 'merge: bring in fast sensor loop' with the tip of turn-left as "
               "first parent and the tip of fast-loop as second parent",
            lambda: merge1 is not None and f.parents(merge1) == [turn, fast], needs_repo=True,
            why=lambda: "no merge commit with that message and those two parents is on main")
    t.check(2, "live repo: that merge commit holds both changes (turn_left in controller.c, timeout 40 in sensor_limits.h)",
            lambda: merge1 is not None and "void turn_left(int degrees)" in (f.file_at(merge1, "src/controller.c") or "")
            and TIMEOUT_40 in (f.file_at(merge1, LIMITS_PATH) or "").splitlines(), needs_repo=True)
    return t


# -- Task 4 -----------------------------------------------------------------
def grade_task4(ctx: Ctx) -> Task:
    """Task 4: a merge conflict, resolved by hand in nano."""
    t = Task(4, "A merge conflict", 40, ctx.repo_mode)
    f = ctx.facts
    fix = f.tips[FIX_BRANCH]
    s41 = ctx.step("4.1")
    t.check(3, "4.1 merge output: CONFLICT (content): Merge conflict in src/sensor_limits.h",
            lambda: re.search(r"CONFLICT \(content\): Merge conflict in src/sensor_limits\.h", s41) is not None)
    t.check(2, "4.1 merge output: Automatic merge failed; fix conflicts and then commit the result.",
            lambda: "Automatic merge failed; fix conflicts and then commit the result." in s41)
    s42 = ctx.step("4.2")
    t.check(2, "4.2 status says You have unmerged paths", lambda: "You have unmerged paths" in s42)
    t.check(2, "4.2 status lists 'both modified:' src/sensor_limits.h",
            lambda: re.search(r"both modified:\s+src/sensor_limits\.h", s42) is not None)
    s43 = ctx.step("4.3")
    t.check(3, "4.3 the file shows the three markers (<<<<<<< , =======, >>>>>>> origin/fix/echo-timeout)",
            lambda: re.search(r"(?m)^<<<<<<< ", s43) is not None and re.search(r"(?m)^=======$", s43) is not None
            and re.search(r"(?m)^>>>>>>> origin/fix/echo-timeout$", s43) is not None)
    t.check(1, "4.3 both competing lines are shown (timeout 40 and timeout 30)",
            lambda: "SENSOR_TIMEOUT_MS 40" in s43 and "SENSOR_TIMEOUT_MS 30" in s43)
    t.check(3, "4.4 the limits check ends with ALL CHECKS PASSED",
            lambda: "ALL CHECKS PASSED" in ctx.step("4.4"))
    s45 = ctx.step("4.5")
    t.check(3, "4.5 commit output: [main sha] merge: settle echo timeout at 30 ms",
            lambda: re.search(r"\[main [0-9a-f]{7,}\] " + re.escape(MERGE2_SUBJECT), s45) is not None)
    s46 = ctx.step("4.6")
    t.check(2, "4.6 graph: the new merge commit is at HEAD -> main",
            lambda: _line_with(s46, "HEAD -> main", MERGE2_SUBJECT))
    t.check(1, "4.6 graph: origin/fix/echo-timeout is on a different line (its commit is now part of main's history)",
            lambda: _line_with(s46, "origin/fix/echo-timeout") and not _line_with(s46, "HEAD -> main", "origin/fix/echo-timeout"))

    merge1 = f.merge_commit(MERGE1_SUBJECT) if ctx.repo_mode else None
    merge2 = f.merge_commit(MERGE2_SUBJECT) if ctx.repo_mode else None
    content = (f.file_at(merge2, LIMITS_PATH) or "") if merge2 else ""
    lines = content.splitlines()
    t.check(5, "live repo: main has the merge commit 'merge: settle echo timeout at 30 ms' whose parents are the first "
               "merge commit and the tip of fix/echo-timeout",
            lambda: merge1 is not None and merge2 is not None and f.parents(merge2) == [merge1, fix],
            needs_repo=True, why=lambda: "that merge commit with those two parents is not on main")
    t.check(3, "live repo: no conflict marker is left in src/sensor_limits.h",
            lambda: bool(content) and not any(line.startswith(("<<<<<<<", "=======", ">>>>>>>")) for line in lines),
            needs_repo=True)
    t.check(3, "live repo: the timeout line is exactly '#define SENSOR_TIMEOUT_MS 30' (Chitra's number)",
            lambda: lines.count(TIMEOUT_30) == 1 and TIMEOUT_40 not in lines, needs_repo=True)
    t.check(3, "live repo: the file carries a line with your name (the person who made the merge commit)",
            lambda: bool(merge2) and bool(f.author_name(merge2)) and f.author_name(merge2) in content,
            needs_repo=True)
    t.check(2, "live repo: src/sensor_limits.h passes every rule of tests/check_limits.py",
            lambda: bool(content) and not limits_problems(content), needs_repo=True,
            why=lambda: "; ".join(limits_problems(content)))
    t.check(1, "live repo: the conflict commit changes only src/sensor_limits.h compared with the first merge",
            lambda: merge1 is not None and merge2 is not None and f.changed_files(merge1, merge2) == [LIMITS_PATH],
            needs_repo=True)
    t.check(1, "live repo: the SHA printed in 4.5 is that merge commit",
            lambda: merge2 is not None and sha_matches((re.findall(r"\[main ([0-9a-f]{7,40})\]", s45) or [""])[-1], merge2),
            needs_repo=True)
    return t


# -- Task 5 -----------------------------------------------------------------
def grade_task5(ctx: Ctx) -> Task:
    """Task 5: wrap up (merged branches, merge commits, ahead of origin)."""
    t = Task(5, "Wrap up", 15, ctx.repo_mode)
    f = ctx.facts
    merged = set(branch_names(ctx.step("5.1")))
    t.check(3, "5.1 branch -r --merged lists origin/main and the three feature branches",
            lambda: {"origin/main"} | {_remote(b) for b in FEATURE_BRANCHES} <= merged)
    merges = oneline_entries(ctx.step("5.2"))
    t.check(3, "5.2 --merges lists exactly your two merge commits",
            lambda: [strip_decoration(e.subject) for e in merges] == [MERGE2_SUBJECT, MERGE1_SUBJECT])
    s53 = ctx.step("5.3")
    st = parse_status(s53)
    t.check(3, "5.3 status: On branch main, ahead of 'origin/main' by 5 commits, working tree clean",
            lambda: "On branch main" in s53 and st.ahead == 5 and st.clean)
    t.check(2, "ANSWER-3 is 5 (how many commits main is now ahead of origin/main)",
            lambda: get_answer_int(ctx.text, 3) == "5")
    t.check(2, "live repo: main has gained the merged work, the working tree is clean and no merge is in progress",
            lambda: f.commits_above_origin() > 0 and f.working_tree_clean(), needs_repo=True)
    t.check(2, "live repo: main is exactly 5 commits above origin/main and contains all three feature branches",
            lambda: f.commits_above_origin() == 5 and all(f.is_ancestor(f.tips[b], f.main_tip()) for b in FEATURE_BRANCHES),
            needs_repo=True)
    return t
