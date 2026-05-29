"""
Tuka PersonaPlex Natural connector.

This connector registers NVIDIA PersonaPlex as a governed, local/open voice
runtime option for Tuka. It does not start the model, download weights, submit
audio, or bypass Hugging Face license approval.
"""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT / "external" / "nvidia-personaplex"
DATA = ROOT / "data"
PROFILE_PATH = DATA / "personaplex_natural_profile.json"
VENV_PYTHON = ROOT / ".venv_personaplex" / "Scripts" / "python.exe"

NATURAL_VOICES = {
    "female": ["NATF0", "NATF1", "NATF2", "NATF3"],
    "male": ["NATM0", "NATM1", "NATM2", "NATM3"],
}


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
        return proc.returncode == 0
    except Exception:
        return False


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


def _torch_cuda_status(python_exe: Path) -> dict[str, Any]:
    if not python_exe.exists():
        return {"checked": False, "reason": "python_missing"}
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
        return {"checked": False, "reason": str(exc)}
    if proc.returncode != 0:
        return {"checked": False, "reason": proc.stderr.strip()[:500]}
    try:
        data = json.loads(proc.stdout.strip())
    except Exception:
        return {"checked": False, "reason": proc.stdout.strip()[:500]}
    data["checked"] = True
    return data


def _env_present(name: str) -> bool:
    value = os.environ.get(name)
    if value:
        return True
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                value, _ = winreg.QueryValueEx(key, name)
                return bool(value)
        except Exception:
            return False
    return False


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
        return {"available": False, "error": str(exc)}
    if proc.returncode != 0:
        return {"available": False, "error": proc.stderr.strip()[:300]}
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
        "name": parts[0] if parts else None,
        "memory_total_mb": memory_mb,
        "driver_version": parts[2] if len(parts) >= 3 else None,
        "cpu_offload_recommended": memory_mb is not None and memory_mb < 16000,
    }


class PersonaPlexNaturalConnector:
    def __init__(self, repo: Path = REPO, profile_path: Path = PROFILE_PATH) -> None:
        self.connector = "tuka_personaplex_natural_connector_v0_1"
        self.repo = Path(repo)
        self.profile_path = Path(profile_path)
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)

    def readiness(self) -> dict[str, Any]:
        readme = self.repo / "README.md"
        moshi_dir = self.repo / "moshi"
        gpu = _gpu_status()
        torch_cuda = _torch_cuda_status(VENV_PYTHON)
        current_deps = {
            "torch": _module_available("torch"),
            "torchaudio": _module_available("torchaudio"),
            "transformers": _module_available("transformers"),
            "accelerate": _module_available("accelerate"),
            "huggingface_hub": _module_available("huggingface_hub"),
            "moshi": _module_available("moshi"),
        }
        venv_deps = {
            "torch": _module_available_in_python(VENV_PYTHON, "torch"),
            "torchaudio": _module_available_in_python(VENV_PYTHON, "torchaudio"),
            "transformers": _module_available_in_python(VENV_PYTHON, "transformers"),
            "accelerate": _module_available_in_python(VENV_PYTHON, "accelerate"),
            "huggingface_hub": _module_available_in_python(VENV_PYTHON, "huggingface_hub"),
            "moshi": _module_available_in_python(VENV_PYTHON, "moshi"),
        }
        deps = {name: current_deps.get(name) or venv_deps.get(name) for name in current_deps}
        blockers = []
        if not self.repo.exists():
            blockers.append("official_repo_missing")
        if not readme.exists():
            blockers.append("readme_missing")
        if not moshi_dir.exists():
            blockers.append("moshi_source_missing")
        if not _env_present("HF_TOKEN"):
            blockers.append("hf_token_missing")
        if not deps["moshi"]:
            blockers.append("moshi_package_not_installed")
        if not deps["torch"]:
            blockers.append("torch_not_installed")
        elif torch_cuda.get("cuda_available") is not True:
            blockers.append("torch_cuda_not_available")
        if not deps["torchaudio"]:
            blockers.append("torchaudio_not_installed")
        if gpu.get("cpu_offload_recommended") and not deps["accelerate"]:
            blockers.append("accelerate_needed_for_cpu_offload")

        profile = {
            "connector": self.connector,
            "updated_at": _now(),
            "public_name": "Tuka Natural Duplex",
            "source_name": "NVIDIA PersonaPlex",
            "source_repo": "https://github.com/NVIDIA/personaplex",
            "model_id": "nvidia/personaplex-7b-v1",
            "mode": "governed_local_open_voice_runtime",
            "natural_voices": NATURAL_VOICES,
            "preferred_tuka_voice_prompt": "NATF2",
            "policy": {
                "copy_provider_code_or_weights": False,
                "requires_model_license_acceptance": True,
                "requires_hf_token": True,
                "no_audio_submission_without_admin": True,
                "no_live_runtime_without_admin_gate": True,
                "use_tuka_native_names_in_ui": True,
            },
            "repo": {
                "path": str(self.repo),
                "exists": self.repo.exists(),
                "readme_exists": readme.exists(),
                "moshi_source_exists": moshi_dir.exists(),
            },
            "venv": {
                "path": str(VENV_PYTHON.parent.parent),
                "python": str(VENV_PYTHON),
                "exists": VENV_PYTHON.exists(),
                "version": _python_version(VENV_PYTHON),
            },
            "dependencies": deps,
            "dependency_sources": {
                "current_interpreter": current_deps,
                "personaplex_venv": venv_deps,
            },
            "gpu": gpu,
            "torch_cuda": torch_cuda,
            "runtime": {
                "live_ready": len(blockers) == 0,
                "blocked": len(blockers) > 0,
                "blockers": blockers,
                "recommended_launch_mode": "moshi.server"
                if platform.system().lower() == "windows" and torch_cuda.get("cuda_available") is True
                else (
                    "moshi.server --cpu-offload"
                    if gpu.get("cpu_offload_recommended")
                    else "moshi.server"
                ),
                "windows_note": "On this Windows RTX 3080 setup, full CUDA launch passed; cpu-offload hit an accelerate meta-tensor path.",
            },
        }
        self.profile_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
        return profile

    def status(self) -> dict[str, Any]:
        profile = self.readiness()
        return {
            "ok": True,
            "connector": self.connector,
            "profile_path": str(self.profile_path),
            "public_name": profile["public_name"],
            "live_ready": profile["runtime"]["live_ready"],
            "blockers": profile["runtime"]["blockers"],
        }


if __name__ == "__main__":
    print(json.dumps(PersonaPlexNaturalConnector().readiness(), indent=2, ensure_ascii=False))
