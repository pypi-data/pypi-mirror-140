from setuptools import setup

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="google-reverse-search",
    version="0.1.3",
    author="Joker Hacker",
    author_email="jokerhacker.6521@protonmail.com",
    packages=["GoogleSearch"],
    description="Simple python library to reverse search any image via file or url",
    license='License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Black-Bulls-Bots/google-reverse-search",
    project_urls = {
        "Discussion" : "https://t.me/blackbulls_support",
    },
    install_requires=[
    "beautifulsoup4",
    "requests",
    "urllib3"
],
    python_requires = ">=3.8"
)
