import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = ["pydantic==1.9.0"]

setuptools.setup(
    name="asyncio_tcp_messages",
    version="0.1.3",
    author_email="UnMelow@yandex.ru",
    description="A library for developing applications with a message-based protocol on top of TCP based on asyncio.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/python-2k2s-2022/asyncio-tasks-submissions/team-4",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
