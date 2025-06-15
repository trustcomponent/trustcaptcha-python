import toml
import os

base_version = "0.0.0"

if "CI_COMMIT_TAG" in os.environ:
    package_version = os.environ["CI_COMMIT_TAG"]
else:
    branch_name = os.getenv('CI_COMMIT_REF_NAME').replace("/", ".")
    commit_sha = os.getenv('CI_COMMIT_SHORT_SHA')
    package_version = f"{base_version}+{branch_name}.{commit_sha}"

with open("pyproject.toml", "r") as f:
    data = toml.load(f)

data["project"]["version"] = package_version

with open("pyproject.toml", "w") as f:
    toml.dump(data, f)

print(f"Version updated to {package_version}")
