from setuptools import setup, find_packages


setup(
    name='c_lancet',
    version='0.0.1',
    author="Peiwei Hu",
    author_email='jlu.hpw@foxmail.com',
    description='A static C source code analysis framework',
    packages=find_packages(),
    package_data={'': ['*.so']},
    include_package_data=True,
    url='https://github.com/PeiweiHu/c_lancet',
    install_requires=[
        'tree-sitter',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
