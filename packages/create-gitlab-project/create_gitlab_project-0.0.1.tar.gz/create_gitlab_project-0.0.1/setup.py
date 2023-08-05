""" Setup file """
from setuptools import setup, find_packages

REQUIREMENTS = [
    "python-gitlab==3.1.0"
]

setup(
    name='create_gitlab_project',
    version='0.0.1',
    description="Gitlab Project Creation CLI",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    license='MIT',
    author="DefineX Labs",
    author_email='labs@teamdefinex.com',
    url="https://teamdefinex.com/",
    keywords="gitlab project creation",
    platforms="any",
    zip_safe=False,
    python_requires=">=3.9",
    include_package_data=True,
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    setup_requires=REQUIREMENTS,
    test_suite='setup.my_test_suite'
)