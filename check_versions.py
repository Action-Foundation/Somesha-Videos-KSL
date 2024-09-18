import importlib
import subprocess

def get_package_version(package_name):
    try:
        return importlib.import_module(package_name).__version__
    except ImportError:
        return "Not installed"
    except AttributeError:
        # Some packages might not have __version__ attribute
        try:
            return subprocess.check_output([package_name, "--version"]).decode().strip()
        except:
            return "Version not found"

packages = ["numpy", "requests", "cv2", "gradio", "vimeo"]

for package in packages:
    version = get_package_version(package)
    print(f"{package}: {version}")