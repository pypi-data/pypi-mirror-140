from setuptools import setup

VERSION = '0.0.3'
DESCRIPTION = 'A package for visualize discord embeds'
LONG_DESCRIPTION = 'A package that allows you to get discord embeds as a image file'
with open('readme.md', 'r') as file:
    LONG_DESCRIPTION = file.read()

setup(
    name="virtualembed",
    version=VERSION,
    author="Fenish",
    author_email="sohretalhadev@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    keywords=['python', 'discord', 'discord_embed', 'embed'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)