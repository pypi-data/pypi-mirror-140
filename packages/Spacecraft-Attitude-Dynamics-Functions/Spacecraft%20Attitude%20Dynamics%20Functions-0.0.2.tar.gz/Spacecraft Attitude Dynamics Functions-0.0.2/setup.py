import setuptools

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setuptools.setup(
    name='Spacecraft Attitude Dynamics Functions',
    version='0.0.2',
    description='Functions for Purdue AAE440 Class',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='https://shivbc.com/',
    author='Shivam Bhatia',
    author_email='shivbhatia19@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='Dynamics',
    package_dir={"":"src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=['numpy','scipy','sympy','matplotlib']
)