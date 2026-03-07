import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
WORKSPACES_DIR = BASE_DIR / "workspaces"
WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class RepoRunResult:
    task_id: str
    repo: str
    workspace_name: str
    workspace_path: str
    cloned: bool
    message: str


def clone_repo(task_id: str, repo: str):
    repo_url = f"https://github.com/{repo}.git"
    repo_name = repo.replace("/", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace_name = f"{repo_name}_{timestamp}"
    workspace_path = WORKSPACES_DIR / workspace_name
    workspace_path.mkdir(parents=True, exist_ok=True)
    target_dir = workspace_path / "repo"

    try:
        subprocess.run(
            ["git", "clone", repo_url, str(target_dir)],
            capture_output=True,
            text=True,
            check=True,
        )

        return RepoRunResult(
            task_id=task_id,
            repo=repo_url,
            workspace_name=workspace_name,
            workspace_path=str(workspace_path),
            cloned=True,
            message="Repository cloned successfully",
        )

    except subprocess.CalledProcessError as e:
        return RepoRunResult(
            task_id=task_id,
            repo=repo_url,
            workspace_name=workspace_name,
            workspace_path=str(workspace_path),
            cloned=False,
            message=e.stderr,
        )

def write_test_file(workspace_path: str):
    repo_dir = Path(workspace_path) / "repo"
    test_file = repo_dir / "TUKA_TEST.txt"

    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Hello from Tuka AI\n")

    return str(test_file)
def _run_cmd(cmd: list[str], cwd: Path):
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=True,
    )


def create_branch(workspace_path: str, branch_name: str):
    repo_dir = Path(workspace_path) / "repo"
    _run_cmd(["git", "checkout", "-b", branch_name], repo_dir)
    return branch_name


def git_commit_all(workspace_path: str, message: str):
    repo_dir = Path(workspace_path) / "repo"

    _run_cmd(["git", "add", "."], repo_dir)

    try:
        _run_cmd(
            [
                "git",
                "-c", "user.name=Tuka AI",
                "-c", "user.email=tuka@example.com",
                "commit",
                "-m", message,
            ],
            repo_dir,
        )
        return {"committed": True, "message": message}
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        stdout = e.stdout or ""

        if "nothing to commit" in stderr.lower() or "nothing to commit" in stdout.lower():
            return {"committed": False, "message": "Nothing to commit"}

        raise


def run_repo_job(task_id: str, repo: str):
    result = clone_repo(task_id, repo)

    if not result.cloned:
        return {
            "ok": False,
            "step": "clone",
            "repo_result": result.__dict__,
        }

    created_file = write_test_file(result.workspace_path)
    branch_name = f"tuka/{task_id}"

    try:
        create_branch(result.workspace_path, branch_name)
    except subprocess.CalledProcessError as e:
        return {
            "ok": False,
            "step": "branch",
            "repo_result": result.__dict__,
            "file_created": created_file,
            "error": e.stderr or str(e),
        }

    try:
        commit_result = git_commit_all(
            result.workspace_path,
            f"Tuka update for task {task_id}",
        )
    except subprocess.CalledProcessError as e:
        return {
            "ok": False,
            "step": "commit",
            "repo_result": result.__dict__,
            "file_created": created_file,
            "branch_name": branch_name,
            "error": e.stderr or str(e),
        }

    return {
        "ok": True,
        "repo_result": result.__dict__,
        "file_created": created_file,
        "branch_name": branch_name,
        "commit_result": commit_result,
    }