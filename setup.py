from setuptools import setup

setup(
    name="mrhat-rtcwake",
    version="0.1.4",
    description="rtcwake like utility to be used on RaspberryPi with the Effective Range MrHat extension board",
    author="Ferenc Nandor Janky & Attila Gombos",
    author_email="info@effective-range.com",
    packages=["rtcwake"],
    scripts=["bin/mrhat-rtcwake"],
    install_requires=[
        "tzlocal",
        "python-context-logger@git+https://github.com/EffectiveRange/python-context-logger.git@latest",
    ],
)
