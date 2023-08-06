import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='aiit_sdk',
    version='0.0.6',
    author='Guoqun Jin',
    author_email='guoqun.jin@hotmail.com',
    description='A python sdk for AIIT OS',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://192.168.140.202/unstructured-etl-group/aiit-sdk.git',
    license='GNU General Public License v3.0',
    project_urls={
        "Bug Tracker": "http://192.168.140.202/unstructured-etl-group/aiit-sdk/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        "requests>=2.25.1",
        "django-cacheops>=5.1",
        "djangorestframework>=3.12.2",
        "djangorestframework-simplejwt>=4.6.0",
    ],
    python_requires=">=3.7"
)
