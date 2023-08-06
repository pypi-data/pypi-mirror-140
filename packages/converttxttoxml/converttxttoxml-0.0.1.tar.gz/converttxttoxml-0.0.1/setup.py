from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='converttxttoxml',
    version='0.0.1',
    description='Txt to xml converter',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Aman Kumar and Param Sharma',
    author_email='aman.kumar@bobble.ai',
    License='MIT',
    classifiers=classifiers,
    keywords='converter',
    package=find_packages(),
    install_requires=['']
)