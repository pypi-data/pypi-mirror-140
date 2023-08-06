from setuptools import setup, find_packages

setup(
    name="TOPSIS-101903452",
    version="0.0.1",
    license="MIT",
    description="A Python package to find TOPSIS for Multi-Criteria Decision Analysis Method",
    long_description=open('README.txt').read() + '\n\n' +
    open('CHANGELOG.txt').read(),
    long_description_content_type="text/markdown",
    author="Priya Aggarwal",
    author_email="aggarwalpriya1121@gmail.com",
    url="https://github.com/Priya2123/Topsis",
    download_url="https://github.com/Priya2123/Topsis/archive/refs/tags/0.0.1.tar.gz",
    keywords=['topsis', 'UCS654', 'TIET'],
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
