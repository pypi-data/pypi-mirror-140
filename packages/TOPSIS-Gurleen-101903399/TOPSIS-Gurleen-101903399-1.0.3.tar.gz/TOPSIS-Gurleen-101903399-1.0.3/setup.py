from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README

setup(
    name="TOPSIS-Gurleen-101903399",
    packages=["Topsis_Ranking"],
    version="1.0.3",
    license="MIT",
    description="A Python package to get best alternative available using TOPSIS method.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Gurleen Kaur",
    author_email="gurleendhillonm1114@gmail.com",
    url="https://github.com/gurleen-kaur1313/topsis",
    classifiers=[
        "Development Status :: 3 - Alpha",      
        "Intended Audience :: Developers",  
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    include_package_data=True,
    install_requires=["pandas"],
    entry_points={
        "console_scripts": [
            "TOPSIS-Gurleen-101903399=Topsis_Ranking.topsis:main",
        ]
    },
)