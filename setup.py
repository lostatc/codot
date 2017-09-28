from setuptools import setup

setup(
    name="codot",
    version="0.1",
    description="Consolidate your dotfiles.",
    url="https://github.com/lostatc/codot",
    author="Garrett Powell",
    author_email="garrett@gpowell.net",
    license="GPLv3",
    install_requires=["Sphinx", "pyinotify", "linotype", "terminaltables"],
    tests_require=["pytest", "pyfakefs"],
    python_requires=">=3.5",
    extras_require={
        "Colored output in Windows": ["colorama"]},
    packages=[
        "codot", "codot.commands"
        ]
    )
