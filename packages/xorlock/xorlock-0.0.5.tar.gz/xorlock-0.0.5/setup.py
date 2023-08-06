from setuptools import setup, find_packages
import codecs
import os


here = os.path.abspath(os.path.dirname(__file__))


with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


VERSION = "0.0.5"
DESCRIPTION = "Encrypt using the XOR encryption method."
LONG_DESCRIPTION = "Encrypt using the XOR encryption method."


setup(
    name="xorlock",
    version=VERSION,
    author="Nyaanity (Sascha Ehret)",
    author_email="no@mail.wow",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=["python", "encryption", "xor", "security", "cryptography"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
