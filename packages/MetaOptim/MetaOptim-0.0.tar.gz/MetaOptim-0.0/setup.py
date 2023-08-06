from setuptools import setup

setup(
    name="MetaOptim",
    version="0.0",
    author="Jie Ren",
    author_email="jieren9806@gmail.com",
    description="A differentiable optimizer.",
    license="Apache License Version 2.0",
    keywords="meta learning",
    url="https://github.com/metaopt/MetaOptim",
    packages=['MetaOptim'],

    install_requires=[
        'torch',
    ],
)
