from setuptools import setup

setup(
    name="homehub-info-service",
    version="1.0.0",
    description="Service to receive informational packets from homehub server.",
    url="https://github.com/claybrooks/homehub-info-service-python",
    author="Clay Brooks",
    author_email="clay_brooks@outlook.com",
    license="Unlicense",
    packages=["infoservice"],
    install_requires=[],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.5",
    ],
)
