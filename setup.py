import os
import re
from setuptools import setup


def read_version():
    init_path = os.path.join(os.path.dirname(__file__), "aim", "__init__.py")
    with open(init_path, "r", encoding="utf-8") as f:
        match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', f.read(), re.MULTILINE)
    if not match:
        raise RuntimeError("Unable to find __version__ in aim/__init__.py")
    return match.group(1)


setup(
    name="aim-cli",
    version=read_version(),
    author="YourClass Academy",
    description="AIM (AI Memory/Mind) CLI - Centralized Project Context & Memory Engine",
    license="MIT",
    packages=["aim"],
    include_package_data=True,
    package_data={
        "aim": [
            "dashboard.html",
            "templates/*",
            "templates/**/*",
            "skills/*",
            "skills/**/*",
        ]
    },
    entry_points={
        "console_scripts": [
            "aim=aim.aim_cli:main",
        ]
    },
    extras_require={
        # Optional embeddings backend for `aim search --semantic` and the
        # doctor similar-memory check. The core stays zero-dependency.
        "semantic": ["sentence-transformers>=2.2"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
