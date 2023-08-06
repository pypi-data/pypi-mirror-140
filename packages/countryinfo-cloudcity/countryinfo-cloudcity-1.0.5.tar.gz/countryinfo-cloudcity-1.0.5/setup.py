import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="countryinfo-cloudcity",
    version="1.0.5",
    packages=setuptools.find_packages(),
    long_description_content_type="text/markdown",
    long_description=long_description,
    python_requires=">=3.9",
    install_requires=[
        "pycountry"
    ],
    url='https://gitlab.com/dqna/countryinfo-cloudcity',
    # include_package_data=True,
    package_data={'cc_country': ['data/*']}
)
