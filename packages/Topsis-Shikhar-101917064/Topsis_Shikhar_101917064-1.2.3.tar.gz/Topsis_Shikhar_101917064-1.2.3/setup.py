from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README

setup(
    name="Topsis_Shikhar_101917064",
    version="1.2.3",
    description="A Python package implementing TOPSIS technique.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Shikhar Garg",
    author_email="shikhargarg15@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["Topsis_Shikhar_101917064"],
    include_package_data=True,
    install_requires=['pandas'
     ],
     entry_points={
        "console_scripts": [
            "topsis=topsis_python.topsis:main",
        ]
     },
)
