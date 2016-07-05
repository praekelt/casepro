from setuptools import setup, find_packages

with open('pip-freeze.txt') as req_file:
    requirements = req_file.read().split('\n')

setup(
    name="casepro",
    version="0.1",
    url='http://github.com/rapidpro/casepro',
    license='BSD',
    author='UNICEF and Individual Contributors',
    author_email='dev@praekeltfoundation.org',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
