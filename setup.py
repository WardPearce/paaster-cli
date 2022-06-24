from setuptools import setup

setup(
    name="paaster",
    version="0.0.1",
    py_modules=["PaasterClient"],
    install_requires=[
        "pyclip",
        "cryptography",
        "requests",
        "plyer",
        "click"
    ],
    entry_points="""
        [console_scripts]
        paaster=PaasterClient:main
    """
)
