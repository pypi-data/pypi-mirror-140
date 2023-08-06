from setuptools import setup

setup(
    name = "dur",
    packages = ["dur"],
    entry_points = {
        "console_scripts": ['dur = dur.dur:main']
        },
    version = "0.3.0",
    description = "Test",
    long_description = "Test",
    author = "Vid Potocnik",
    author_email = "vidpotocnik.osebni@gmail.com",
    url = ""
    )