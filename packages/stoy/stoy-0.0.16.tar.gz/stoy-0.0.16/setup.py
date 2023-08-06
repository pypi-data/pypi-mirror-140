import setuptools
import os


with open("README.md", "r") as fh:
    long_description = fh.read()


PATH = os.path.dirname(__file__)


def get_version():
    with open(os.path.join(PATH, "stoy", "VERSION")) as version_file:
        version = version_file.read().strip()
    return version


setuptools.setup(
    name="stoy",
    version=get_version(),
    author="Roman Kosobrodov",
    author_email="roman@kosobrodov.net",
    description="Jupyter Server auto stop",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RomanKosobrodov/stoy",
    packages=setuptools.find_packages(),
    package_data={
        'stoy': ["VERSION"]
    },
    scripts=["bin/stoy", "bin/generate-token"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    install_requires=["aiohttp>=3.8", "boto3>=1.20"]
)
