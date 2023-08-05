from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='verdata',
    version='1',
    description='Veri şifreleme',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='',
    author='Testere_necmi',
    author_email='',
    license='MIT',
    classifiers=classifiers,
    keywords='verdata',
    packages=find_packages()
)
