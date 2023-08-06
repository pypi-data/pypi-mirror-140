import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

description = (
    'A middleware for Dramatiq (for Django) that keeps track of '
    'task state only when you need it to.'
)

setuptools.setup(
    name='dramatiq-taskstate',
    version='0.3.3',
    author='Armandt van Zyl',
    author_email='armandtvz@gmail.com',
    description=description,
    license='GPL-3.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/armandtvz/dramatiq-taskstate',
    packages=setuptools.find_packages(exclude=['test_proj', 'test_project']),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
    ],
    python_requires='>=3.6',
    install_requires=[
        'Django>=3.2',
        'dramatiq>=1.11',
        'django_dramatiq>=0.10',
        'psycopg2-binary',
    ],
    extras_require = {
        'websockets': [
            'channels',
            'redis',
        ]
    }
)
