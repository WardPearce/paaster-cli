from setuptools import setup, find_packages


def get_long_description():
    with open("README.md", encoding="utf8") as f:
        return f.read()


setup(
    name="paaster",
    version="0.0.3",
    url="https://github.com/WardPearce/paaster-cli",
    author="WardPearce",
    author_email="wardpearce@pm.me",
    description=(
        "Upload locally encrypted pastes to "
        "paaster.io from your desktop."
    ),
    license="GPL-3.0",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    py_modules=["PaasterCLI"],
    install_requires=[
        "pyperclip",
        "cryptography",
        "requests",
        "click"
    ],
    entry_points="""
        [console_scripts]
        paaster=PaasterCLI:main
    """,
    packages=find_packages(),
    python_requires=">=3.6",
    include_package_data=True,
    zip_safe=False
)
