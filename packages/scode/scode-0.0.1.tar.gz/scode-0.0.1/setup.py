import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="scode", # Replace with your own username
    version="0.0.1",
    author="강동욱, 선준우, 강진영, 박태준, 김도현",
    author_email="ehddnr2981@gmail.com",
    description="The Private Package of Showm Company.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/showm-dev/Standard",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)