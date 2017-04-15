from setuptools import setup

setup(
    name="codot",
    version="0.1",
    description="Consolidate your dotfiles.",
    url="https://github.com/lostatc/codot",
    author="Garrett Powell",
    author_email="garrett@gpowell.net",
    license="GPLv3",
    install_requires=["Sphinx", "pyinotify"],
    python_requires=">=3.5",
    data_files=[
        ("bin",
            ["scripts/codot", "scripts/codotd"]),
        ("share/licenses/codot",
            ["LICENSE"]),
        ("share/codot",
            ["docs/config/settings.conf"]),
        ("lib/systemd/user",
            ["docs/unit/codot.service"]),
        ("share/man/man1",
            ["docs/_build/man/codot.1"])
        ],
    packages=[
        "codot", "codot.commands"
        ]
    )
