import importlib
import subprocess
import sys

def get_package_version(package_name):
    try:
        return importlib.import_module(package_name).__version__
    except ImportError:
        return "Not installed"
    except AttributeError:
        # Some packages might not have __version__ attribute
        try:
            return subprocess.check_output([sys.executable, "-m", "pip", "show", package_name]).decode().split("\n")[1].split(": ")[1]
        except:
            return "Version not found"

packages = [
    "numpy",
    "requests",
    "opencv-python-headless",
    "gradio",
    "vimeo",
    "PyVimeo",
    "fastapi",
    "pydantic",
    "uvicorn"
]

print(f"Python version: {sys.version.split()[0]}")

for package in packages:
    version = get_package_version(package)
    print(f"{package}: {version}")