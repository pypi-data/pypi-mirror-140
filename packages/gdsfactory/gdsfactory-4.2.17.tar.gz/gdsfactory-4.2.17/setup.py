from setuptools import find_packages, setup


def get_install_requires():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f.readlines() if not line.startswith("-")]


def get_install_requires_dev():
    with open("requirements_dev.txt", "r") as f:
        return [line.strip() for line in f.readlines() if not line.startswith("-")]


def get_install_requires_full():
    with open("requirements_full.txt", "r") as f:
        return [line.strip() for line in f.readlines() if not line.startswith("-")]


with open("README.md") as f:
    LONG_DESCRIPTION = f.read()


setup(
    name="gdsfactory",
    url="https://github.com/gdsfactory/gdsfactory",
    version="4.2.17",
    author="gdsfactory community",
    scripts=["gdsfactory/gf.py"],
    description="python library to generate GDS layouts",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_install_requires(),
    python_requires=">=3.7",
    license="MIT",
    entry_points="""
        [console_scripts]
        gf=gdsfactory.gf:gf
    """,
    extras_require={
        "full": list(set(get_install_requires() + get_install_requires_full())),
        "basic": get_install_requires(),
        "dev": list(
            set(
                get_install_requires()
                + get_install_requires_dev()
                + get_install_requires_full()
            )
        ),
    },
)
