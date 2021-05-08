from setuptools import setup
from setuptools import find_packages


setup(
    name='edgar-utils',
    version=open('edgar-utils.version').read(),
    author='Aleksey Beregov',
    author_email='beregov@teladictum.com',
    packages=find_packages(include=['*']),
    python_requires='>=3.6',
    url='https://pypi.org/project/edgar-utils/',
    license='LICENSE.txt',
    description='Utils to load financials filing from Edgar',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "pytest",
        "pytest-cov",
        "faker",
        "parse",
        "requests",
        "sphinx"
    ],
    classifiers=[
        # 3 - Alpha, 4 - Beta, 5 - Production/Stable
        'Development Status :: 4 - Beta',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        # Specify the Python versions you support here.
        'Programming Language :: Python :: 3.6',
    ],
)