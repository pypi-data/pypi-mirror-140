from setuptools import setup

setup(
    name="battlesnake_builder",
    version="0.1.1",
    description="Easily build a BattleSnake",
    long_description=open("./README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    author="Johannes Pour",
    url="https://github.com/Tch1b0/battlesnake-builder",
    author_email="Johannes@ben11.de",
    packages=["battlesnake_builder"],
    requires=["Flask"]
)
