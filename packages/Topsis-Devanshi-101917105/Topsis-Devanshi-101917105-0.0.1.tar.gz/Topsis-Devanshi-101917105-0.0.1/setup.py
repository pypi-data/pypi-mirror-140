from setuptools import setup, find_packages

setup(
    name="Topsis-Devanshi-101917105",
    version="0.0.1",
    license="MIT",
    description="A Python package to find TOPSIS for multi-criteria decision analysis method",
    author="Devanshi",
    author_email="ddevanshi_be19@thapar.edu",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pandas', 'tabulate'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ]
)
