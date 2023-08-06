import setuptools

with open("README.rst", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="arclet-alconna",
    version="0.6.4",
    author="ArcletProject",
    author_email="rf_tar_railt@qq.com",
    description="A Fast Command Analyser based on Dict",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/rst",
    url="https://github.com/ArcletProject/Alconna",
    packages=['arclet.alconna'],
    entry_points={
        'console_scripts': [
            'alconna = arclet.alconna.__main__:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    keywords=['command', 'argparse', 'dict', 'fast', 'alconna'],
    python_requires='>=3.8'
)
