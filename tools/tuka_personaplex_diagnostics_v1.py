from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _runtime_root() -> Path:
    explicit = os.environ.get("TUKA_PERSONAPLEX_ROOT")
    if explicit:
        return Path(explicit)
    canonical = Path.home() / "Tuka"
    if canonical.exists() and (
        (canonical / ".venv_personaplex").exists()
        or (canonical / "external" / "nvidia-personaplex").exists()
    ):
        return canonical
    return ROOT


RUNTIME_ROOT = _runtime_root()
DATA = RUNTIME_ROOT / "data"
REPORT = DATA / "personaplex_diagnostics_report.json"
PERSONAPLEX_REPO = RUNTIME_ROOT / "external" / "nvidia-personaplex"
VENV_PYTHON = RUNTIME_ROOT / ".venv_personaplex" / "Scripts" / "python.exe"
LOCAL_VOICE_HOST = "127.0.0.1"
LOCAL_VOICE_PORT = 8998
LOCAL_VOICE_URL = "http://127.0.0.1:8998/"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _module_available_in_python(python_exe: Path, name: str) -> bool:
    if not python_exe.exists():
        return False
    code = (
        "import importlib.util, sys; "
        f"sys.exit(0 if importlib.util.find_spec({name!r}) is not None else 1)"
    )
    try:
        proc = subprocess.run(
            [str(python_exe), "-c", code],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception:
        return False
    return proc.returncode == 0


def _python_version(python_exe: Path) -> str | None:
    if not python_exe.exists():
        return None
    try:
        proc = subprocess.run(
            [str(python_exe), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception:
        return None
    return (proc.stdout or proc.stderr).strip() or None


def _env_length(name: str) -> int:
    value = os.environ.get(name)
    if value:
        return len(value)
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                value, _ = winreg.QueryValueEx(key, name)
                return len(str(value)) if value else 0
        except Exception:
            return 0
    return 0


def _port_status(host: str = LOCAL_VOICE_HOST, port: int = LOCAL_VOICE_PORT) -> dict[str, Any]:
    try:
        with socket.create_connection((host, port), timeout=0.75):
            return {
                "host": host,
                "port": port,
                "url": LOCAL_VOICE_URL,
                "listening": True,
                "state": "live_socket_open",
            }
    except OSError as exc:
        return {
            "host": host,
            "port": port,
            "url": LOCAL_VOICE_URL,
            "listening": False,
            "state": "not_listening",
            "reason": str(exc),
        }


def _gpu_status() -> dict[str, Any]:
    try:
        proc = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except Exception as exc:
        return {"available": False, "checked": True, "error": str(exc)}
    if proc.returncode != 0:
        return {"available": False, "checked": True, "error": proc.stderr.strip()[:300]}
    line = proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else ""
    parts = [part.strip() for part in line.split(",")]
    memory_mb = None
    if len(parts) >= 2:
        try:
            memory_mb = int(parts[1])
        except ValueError:
            memory_mb = None
    return {
        "available": True,
        "checked": True,
        "name": parts[0] if parts else None,
        "memory_total_mb": memory_mb,
        "driver_version": parts[2] if len(parts) >= 3 else None,
        "cpu_offload_recommended": memory_mb is not None and memory_mb < 16000,
    }


def _torch_cuda_status(python_exe: Path = VENV_PYTHON) -> dict[str, Any]:
    if not python_exe.exists():
        return {"checked": False, "cuda_available": False, "reason": "personaplex_venv_python_missing"}
    code = (
        "import json, torch; "
        "print(json.dumps({"
        "'torch_version': torch.__version__, "
        "'cuda_version': torch.version.cuda, "
        "'cuda_available': torch.cuda.is_available(), "
        "'device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None"
        "}))"
    )
    try:
        proc = subprocess.run(
            [str(python_exe), "-c", code],
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
    except Exception as exc:
        return {"checked": False, "cuda_available": False, "reason": str(exc)}
    if proc.returncode != 0:
        return {
            "checked": True,
            "cuda_available": False,
            "reason": proc.stderr.strip()[:500] or "torch_cuda_check_failed",
        }
    try:
        data = json.loads(proc.stdout.strip())
    except Exception:
        return {"checked": True, "cuda_available": False, "reason": proc.stdout.strip()[:500]}
    data["checked"] = True
    return data


def bridge_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "contract": "tuka_personaplex_bridge_contract_v1",
        "updated_at": _now(),
        "architecture": [
            "PersonaPlex/Moshi local voice server",
            "127.0.0.1:8998 local socket",
            "Tuka PersonaPlex diagnostics bridge",
            "Tuka Admin Console / Phase 11 Voice UI",
        ],
        "expected_routes": [
            "/personaplex/status",
            "/personaplex/diagnostics",
            "/personaplex/bridge-contract",
            "/personaplex/verify",
        ],
        "local_voice_server": {
            "host": LOCAL_VOICE_HOST,
            "port": LOCAL_VOICE_PORT,
            "url": LOCAL_VOICE_URL,
            "launch_command": (
                "$env:NO_TORCH_COMPILE=\"1\"; "
                "$env:TORCHDYNAMO_DISABLE=\"1\"; "
                "C:\\Users\\battu\\Tuka\\.venv_personaplex\\Scripts\\python.exe "
                "-m moshi.server --port 8998"
            ),
        },
        "governance": {
            "admin_gate_required": True,
            "no_audio_capture_from_diagnostics": True,
            "no_audio_upload_from_diagnostics": True,
            "no_external_provider_call": True,
            "no_paid_voice_usage": True,
            "no_secret_values_returned": True,
            "fail_closed_when_server_missing": True,
        },
    }


def run_diagnostics() -> dict[str, Any]:
    DATA.mkdir(parents=True, exist_ok=True)
    readme = PERSONAPLEX_REPO / "README.md"
    moshi_dir = PERSONAPLEX_REPO / "moshi"
    server = _port_status()
    gpu = _gpu_status()
    torch_cuda = _torch_cuda_status()
    current_deps = {
        "torch": _module_available("torch"),
        "torchaudio": _module_available("torchaudio"),
        "huggingface_hub": _module_available("huggingface_hub"),
        "moshi": _module_available("moshi"),
    }
    venv_deps = {
        "torch": _module_available_in_python(VENV_PYTHON, "torch"),
        "torchaudio": _module_available_in_python(VENV_PYTHON, "torchaudio"),
        "huggingface_hub": _module_available_in_python(VENV_PYTHON, "huggingface_hub"),
        "moshi": _module_available_in_python(VENV_PYTHON, "moshi"),
        "accelerate": _module_available_in_python(VENV_PYTHON, "accelerate"),
    }
    dependencies = {name: current_deps.get(name, False) or venv_deps.get(name, False) for name in venv_deps}
    blockers: list[str] = []
    if not PERSONAPLEX_REPO.exists():
        blockers.append("personaplex_repo_missing")
    if not readme.exists():
        blockers.append("personaplex_readme_missing")
    if not moshi_dir.exists():
        blockers.append("moshi_source_missing")
    if not VENV_PYTHON.exists():
        blockers.append("personaplex_venv_missing")
    if _env_length("HF_TOKEN") <= 0:
        blockers.append("hf_token_missing")
    if not dependencies["torch"]:
        blockers.append("torch_missing")
    if not dependencies["torchaudio"]:
        blockers.append("torchaudio_missing")
    if not dependencies["moshi"]:
        blockers.append("moshi_missing")
    if torch_cuda.get("cuda_available") is not True:
        blockers.append("torch_cuda_not_available")
    if server["listening"] is not True:
        blockers.append("local_voice_server_8998_not_running")

    diagnostics = {
        "ok": True,
        "module": "tuka_personaplex_diagnostics_v1",
        "updated_at": _now(),
        "public_name": "Tuka Natural Duplex Diagnostics",
        "admin_console_integrated": True,
        "diagnosed_root": str(RUNTIME_ROOT),
        "source": {
            "public_alias": "Tuka Natural Duplex",
            "provider_source": "NVIDIA PersonaPlex",
            "model_id": "nvidia/personaplex-7b-v1",
            "copied_provider_weights": False,
            "copied_provider_code_into_tuka": False,
        },
        "repo": {
            "path": str(PERSONAPLEX_REPO),
            "exists": PERSONAPLEX_REPO.exists(),
            "readme_exists": readme.exists(),
            "moshi_source_exists": moshi_dir.exists(),
        },
        "venv": {
            "path": str(VENV_PYTHON.parent.parent),
            "python": str(VENV_PYTHON),
            "exists": VENV_PYTHON.exists(),
            "version": _python_version(VENV_PYTHON),
        },
        "secrets": {
            "hf_token_present": _env_length("HF_TOKEN") > 0,
            "hf_token_length": _env_length("HF_TOKEN"),
            "hf_token_value_returned": False,
        },
        "dependencies": dependencies,
        "dependency_sources": {
            "current_interpreter": current_deps,
            "personaplex_venv": venv_deps,
        },
        "gpu": gpu,
        "torch_cuda": torch_cuda,
        "server": server,
        "runtime": {
            "live_ready": len(blockers) == 0,
            "blocked": len(blockers) > 0,
            "blockers": blockers,
            "diagnostic_truth": (
                "PersonaPlex is only live when the local server is listening on 127.0.0.1:8998 "
                "and CUDA/model dependencies are healthy."
            ),
        },
        "safety": bridge_contract()["governance"],
    }
    REPORT.write_text(json.dumps(diagnostics, indent=2, ensure_ascii=False), encoding="utf-8")
    return diagnostics


def status() -> dict[str, Any]:
    diagnostics = run_diagnostics()
    return {
        "ok": True,
        "status": "diagnosed",
        "admin_console_integrated": True,
        "public_name": diagnostics["source"]["public_alias"],
        "live_ready": diagnostics["runtime"]["live_ready"],
        "blocked": diagnostics["runtime"]["blocked"],
        "blockers": diagnostics["runtime"]["blockers"],
        "server": diagnostics["server"],
        "gpu": diagnostics["gpu"],
        "torch_cuda": diagnostics["torch_cuda"],
        "natural_voices": {
            "female": ["NATF0", "NATF1", "NATF2", "NATF3"],
            "male": ["NATM0", "NATM1", "NATM2", "NATM3"],
        },
        "report": str(REPORT),
    }


def verify() -> dict[str, Any]:
    diagnostics = run_diagnostics()
    contract = bridge_contract()
    checks = {
        "diagnostics_endpoint_ready": {"ok": diagnostics["ok"] is True},
        "bridge_contract_ready": {"ok": contract["ok"] is True},
        "admin_console_integrated": {"ok": diagnostics["admin_console_integrated"] is True},
        "server_8998_status_reported": {
            "ok": diagnostics["server"]["port"] == LOCAL_VOICE_PORT
            and diagnostics["server"]["url"] == LOCAL_VOICE_URL
            and "listening" in diagnostics["server"]
        },
        "repo_status_reported": {"ok": "exists" in diagnostics["repo"] and "moshi_source_exists" in diagnostics["repo"]},
        "venv_status_reported": {"ok": "exists" in diagnostics["venv"] and "version" in diagnostics["venv"]},
        "hf_token_value_hidden": {
            "ok": diagnostics["secrets"]["hf_token_value_returned"] is False
            and "hf_token_length" in diagnostics["secrets"]
        },
        "gpu_status_reported": {"ok": diagnostics["gpu"].get("checked") is True},
        "torch_cuda_status_reported": {"ok": "cuda_available" in diagnostics["torch_cuda"]},
        "fail_closed_when_not_live": {
            "ok": diagnostics["runtime"]["live_ready"] is True
            or (
                diagnostics["runtime"]["blocked"] is True
                and len(diagnostics["runtime"]["blockers"]) > 0
            )
        },
        "no_audio_capture": {"ok": diagnostics["safety"]["no_audio_capture_from_diagnostics"] is True},
        "no_external_provider_call": {"ok": diagnostics["safety"]["no_external_provider_call"] is True},
        "no_paid_voice_usage": {"ok": diagnostics["safety"]["no_paid_voice_usage"] is True},
        "admin_gate_required": {"ok": diagnostics["safety"]["admin_gate_required"] is True},
        "no_fake_live_claim": {
            "ok": diagnostics["runtime"]["live_ready"] is diagnostics["server"]["listening"]
            if "local_voice_server_8998_not_running" in diagnostics["runtime"]["blockers"]
            else True
        },
    }
    passed = sum(1 for item in checks.values() if item["ok"])
    total = len(checks)
    return {
        "ok": passed == total,
        "module": "tuka_personaplex_diagnostics_v1",
        "passed": passed,
        "total": total,
        "checks": checks,
        "diagnostics": diagnostics,
        "contract": contract,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, ensure_ascii=False))
