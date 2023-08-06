import textwrap

from setuptools import setup, find_packages

with open("README.rst") as f:
    readme = f.read()

setup(
    name="lithic",
    description="Lithic API client",
    long_description=readme,
    packages=find_packages(),
    use_scm_version=True,
    author="Kamil Sindi",
    author_email="kamil@lithic.com",
    url="https://github.com/lithic-com/lithic-python",
    keywords="cards issuing api".split(),
    license="MIT",
    setup_requires=["setuptools_scm"],
    include_package_data=True,
    zip_safe=False,
    classifiers=textwrap.dedent(
        """
        Development Status :: 4 - Beta
        Intended Audience :: Developers
        License :: OSI Approved :: Apache Software License
        Environment :: Console
        Programming Language :: Python :: 3.6
        Programming Language :: Python :: 3.7
        Programming Language :: Python :: 3.8
        """
    )
    .strip()
    .splitlines(),
    python_requires=">=3.6",
)
