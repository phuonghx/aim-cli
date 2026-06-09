import os
from setuptools import setup

setup(
    name="aim-cli",
    version="0.1.1",
    author="YourClass Academy",
    description="AIM (AI Memory/Mind) CLI - Centralized Project Context & Memory Engine",
    package_dir={"aim": "."},
    packages=["aim"],
    include_package_data=True,
    package_data={
        "aim": [
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
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
