from setuptools import setup, find_packages

setup(
    name="Topsis-Shubham-101917104",
    version="0.0.1",
    license="MIT",
    description="A Python package to find TOPSIS for multi-criteria decision analysis method",
    author="Shubham Jindal",
    author_email="shubhamjindal410@gmail.com",
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
