from setuptools import setup,find_packages
setup(
    name="hexor",
    version="0.0.10",
    author="YasserBDJ96",
    author_email="yasser.bdj96@gmail.com",
    description='''Coloring texts and their backgrounds in command line interface (cli), with rgb or hex types.''',
    long_description_content_type="text/markdown",
    long_description=open('README.md','r').read(),
    license='''MIT License''',
    packages=find_packages(),
    project_urls={
        'Source Code': "https://github.com/yasserbdj96/hexor",
        'Author WebSite': "https://yasserbdj96.github.io/",
        'Instagram': "https://www.instagram.com/yasserbdj96/",
    },
    install_requires=[],
    keywords=['yasserbdj96', 'python', 'hexor', 'texts', 'colors.', 'hex','background', 'rgb'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Topic :: Communications :: Email'
    ],
    python_requires=">=3.x.x"
)