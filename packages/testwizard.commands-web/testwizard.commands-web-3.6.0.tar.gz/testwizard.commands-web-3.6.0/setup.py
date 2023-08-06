import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="testwizard.commands-web",
    version="3.6.0",
    author="Eurofins Digital Testing - Belgium",
    author_email="testwizard-support@eurofins-digitaltesting.com",
    description="Testwizard Web commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.eurofins-digitaltesting.com/testwizard/",
    packages=['testwizard.commands_web'],
    install_requires=[
        'testwizard.commands-core==3.6.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.3",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
    ],
)













