from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as f:
       LONG_DESCRIPTION = f.read()

# Setting up
setup(
        name="analysishelper",
        version="0.0.5",
        python_requires=">=3.6",
        author="codenamewei",
        author_email="<codenamewei@gmail.com>",
        description='The help you need in data analysis',
        long_description=LONG_DESCRIPTION,
        package_dir={"": "src"},
        packages=find_packages(where="src"),
        install_requires=['pandas>=1.1.5','numpy>1.21'],
        include_package_data=True,
        long_description_content_type="text/markdown",
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ]
)
