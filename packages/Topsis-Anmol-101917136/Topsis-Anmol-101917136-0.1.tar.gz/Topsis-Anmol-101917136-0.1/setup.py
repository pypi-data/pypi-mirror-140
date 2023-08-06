from setuptools import setup

setup(
    name="Topsis-Anmol-101917136",
    version="0.1",
    description="A Python package implementing TOPSIS technique.",
    long_description_content_type="text/markdown",
    author="Anmol Tiwari",
    author_email="atiwari4_be19@thapar.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=['numpy',
                      'pandas'
                      ],
    entry_points={
        "console_scripts": [
            "topsis=topsis.topsis:main",
        ]
    },
)