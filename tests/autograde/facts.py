"""Ground truth about the repository: the published branches and the student's live repo."""
from __future__ import annotations

import os
import re
import subprocess
from typing import Dict, List, NamedTuple, Optional, Set, Tuple

STAFF_SUBJECT = "chore: add lab assignment and grader"
TURN_SUBJECT = "feat(control): add left turn routine"
FAST_SUBJECT = "perf(sensor): shorten echo timeout to 40 ms"
FIX_SUBJECT = "fix(sensor): set echo timeout to 30 ms"
MERGE1_SUBJECT = "merge: bring in fast sensor loop"
MERGE2_SUBJECT = "merge: settle echo timeout at 30 ms"
TURN_BRANCH, FAST_BRANCH, FIX_BRANCH = "feature/turn-left", "feature/fast-loop", "fix/echo-timeout"
FEATURE_BRANCHES = (TURN_BRANCH, FAST_BRANCH, FIX_BRANCH)
LIMITS_PATH = "src/sensor_limits.h"
FAR_ECHO_MS, NO_ECHO_MS = 20, 60
GIT_TIMEOUT = 60
MARKER_PREFIXES = ("<<<<<<<", "=======", ">>>>>>>")
TIMEOUT_RE = re.compile(r"^#define SENSOR_TIMEOUT_MS (\d+)$")


class GitError(RuntimeError):
    """Raised when the repository is not set up the way the grader expects."""


class Commit(NamedTuple):
    """A published commit."""

    sha: str
    author: str
    email: str
    subject: str


def run_git_rc(repo: str, *args: str) -> Tuple[int, str]:
    """Run git in 'repo' and return (exit code, stdout); a git call that hangs is stopped and reported as 124."""
    env = dict(os.environ, LC_ALL="C", GIT_PAGER="cat", GIT_TERMINAL_PROMPT="0")
    try:
        proc = subprocess.run(["git", *args], cwd=repo, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, encoding="utf-8", errors="replace", timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return 124, ""
    return proc.returncode, proc.stdout


def run_git(repo: str, *args: str) -> str:
    """Run git in 'repo' and return stdout ('' on failure)."""
    return run_git_rc(repo, *args)[1]


def limits_problems(text: str) -> List[str]:
    """What is wrong with the text of src/sensor_limits.h (the grader's own copy of tests/check_limits.py).

    Nothing the student wrote is executed: the file is only read as text."""
    lines = text.splitlines()
    problems: List[str] = []
    if any(line.startswith(MARKER_PREFIXES) for line in lines):
        problems.append("merge markers are still in the file")
    timeouts = [int(m.group(1)) for m in (TIMEOUT_RE.match(line) for line in lines) if m]
    if len(timeouts) != 1:
        problems.append("the file must hold exactly one '#define SENSOR_TIMEOUT_MS <number>' line")
    elif timeouts[0] < FAR_ECHO_MS or timeouts[0] >= NO_ECHO_MS:
        problems.append(f"the timeout {timeouts[0]} must be at least {FAR_ECHO_MS} and below {NO_ECHO_MS}")
    if "#define SENSOR_MAX_CM 400" not in lines or "#define SENSOR_MIN_CM 2" not in lines:
        problems.append("SENSOR_MAX_CM or SENSOR_MIN_CM was changed")
    return problems


class Facts:
    """Everything the grader needs to know about the repository. Read-only: never changes the repo."""

    def __init__(self, repo: str) -> None:
        self.repo = repo
        if run_git_rc(repo, "rev-parse", "--verify", "-q", "origin/main^{commit}")[0] != 0:
            raise GitError("origin/main not found. Run the grader inside your clone of the lab repository "
                           "(a clone made with 'git clone ...').")
        raw = run_git(repo, "log", "origin/main", "--format=%H%x1f%an%x1f%ae%x1f%s")
        self.published: List[Commit] = [Commit(*line.split("\x1f")) for line in raw.splitlines() if line.strip()]
        self.origin_tip: str = self.published[0].sha
        self.tips: Dict[str, str] = {}
        for branch in FEATURE_BRANCHES:
            tip = self.rev(f"origin/{branch}")
            if not tip:
                raise GitError(f"origin/{branch} not found. Clone the lab repository again with 'git clone': "
                               "the three feature branches must be there.")
            self.tips[branch] = tip

    # -- published history -------------------------------------------------------------
    def published_emails(self) -> Set[str]:
        """E-mail addresses of the people who wrote the published history and the three branches."""
        return {c.email.lower() for c in self.published} | self._branch_authors(1)

    def published_names(self) -> Set[str]:
        """Names of the people who wrote the published history and the three branches."""
        return {c.author.lower() for c in self.published} | self._branch_authors(0)

    def _branch_authors(self, index: int) -> Set[str]:
        out: Set[str] = set()
        for tip in self.tips.values():
            fields = run_git(self.repo, "show", "-s", "--format=%an%x1f%ae", tip).strip().split("\x1f")
            if len(fields) == 2:
                out.add(fields[index].lower())
        return out

    # -- the student's live repository -------------------------------------------------
    def config_value(self, key: str) -> str:
        """Value of a repository-local config key ('' if unset)."""
        return run_git(self.repo, "config", "--local", "--get", key).strip()

    def rev(self, ref: str) -> str:
        """Full SHA of 'ref' ('' if it does not name a commit)."""
        return run_git(self.repo, "rev-parse", "--verify", "-q", f"{ref}^{{commit}}").strip()

    def commit_exists(self, token: str) -> bool:
        """True if 'token' names a commit object in this repository."""
        return run_git_rc(self.repo, "cat-file", "-e", f"{token}^{{commit}}")[0] == 0

    def author_name(self, sha: str) -> str:
        """Author name recorded in commit 'sha' (the identity the student really committed with)."""
        return run_git(self.repo, "show", "-s", "--format=%an", sha).strip()

    def parents(self, sha: str) -> List[str]:
        """Full SHAs of the parents of 'sha' (empty for a root commit or an unknown commit)."""
        return run_git(self.repo, "show", "-s", "--format=%P", sha).split()

    def file_at(self, ref: str, path: str) -> Optional[str]:
        """Content of 'path' at 'ref' (None if absent)."""
        code, out = run_git_rc(self.repo, "show", f"{ref}:{path}")
        return out if code == 0 else None

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        """True if commit 'ancestor' is 'descendant' itself or part of its history."""
        return run_git_rc(self.repo, "merge-base", "--is-ancestor", ancestor, descendant)[0] == 0

    def head_reflog(self) -> List[str]:
        """HEAD reflog messages, newest first."""
        return run_git(self.repo, "log", "-g", "--format=%gs", "HEAD").splitlines()

    def main_tip(self) -> str:
        """Full SHA of the local branch main ('' if there is none)."""
        return self.rev("refs/heads/main")

    def first_parent_chain(self) -> List[str]:
        """Commits that main added on top of the published tip, following first parents, oldest first."""
        return run_git(self.repo, "rev-list", "--first-parent", "--reverse", f"{self.origin_tip}..refs/heads/main").split()

    def commits_above_origin(self) -> int:
        """Number of commits on main that origin/main does not have."""
        out = run_git(self.repo, "rev-list", "--count", f"{self.origin_tip}..refs/heads/main").strip()
        return int(out) if out.isdigit() else -1

    def merge_commit(self, subject: str) -> Optional[str]:
        """Full SHA of the newest merge commit on main with exactly this subject (None if there is none)."""
        out = run_git(self.repo, "log", "refs/heads/main", "--merges", "--format=%H%x1f%s")
        for line in out.splitlines():
            sha, _, subj = line.partition("\x1f")
            if subj == subject:
                return sha
        return None

    def changed_files(self, base: str, tip: str) -> List[str]:
        """Names of the files that differ between two commits."""
        return run_git(self.repo, "diff", "--name-only", base, tip).split()

    def working_tree_clean(self) -> bool:
        """True when 'git status --porcelain' prints nothing and no merge is in progress."""
        clean = run_git(self.repo, "status", "--porcelain").strip() == ""
        merging = run_git_rc(self.repo, "rev-parse", "-q", "--verify", "MERGE_HEAD")[0] == 0
        return clean and not merging
