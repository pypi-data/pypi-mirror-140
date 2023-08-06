from setuptools import setup, find_packages
import firebrick


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
    
    
setup(
    name='Firebrick',
    version=firebrick.__version__,
    author='Logtism',
    description='Django utilitys',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    install_requires=[
        'django',
        'click'
    ],
    packages=find_packages(),
    python_requires=">=3.9",
    include_package_data=True
)