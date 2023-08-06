import setuptools

with open("README.md", "r") as file_obj:
    long_description = file_obj.read()

install_requires = [
    "confluent-kafka[avro]==1.7.0",
    "prometheus_client",
    "psutil",
    "python-dateutil",
    "python_eloqua_wrapper",
    "python-dotenv",
    "virtualenv",
    "virtualenv-api",
    "lbry-rocksdb",
    "pytz",
    "requests",
    "pyyaml",
    "python-box",
]

dev_requires = install_requires + [
    "pip-tools",
    "pytest",
    "pytest-cov",
    "twine",
    "time-machine",
]

packages = setuptools.find_packages()

setuptools.setup(
    name="nubium-utils",
    version="2.1.0-dev1",
    author="Edward Brennan",
    author_email="ebrennan@redhat.com",
    description="Some Kafka utility functions and patterns for the nubium project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.corp.redhat.com/mkt-ops-de/nubium-utils.git",
    packages=packages,
    install_requires=install_requires,
    include_package_data=True,
    extras_require={"dev": dev_requires},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
