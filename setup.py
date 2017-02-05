from setuptools import setup, find_packages


setup(
    name='pgcsv',
    version='0.1',
    description="CSV to Postgres data puncher.",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='files walk index survey',
    author='Friedrich Lindenberh',
    author_email='friedrich@pudo.org',
    url='http://github.com/pudo/pgcsv',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    package_data={},
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        'six',
        'click',
        'psycopg2',
        'unicodecsv',
        'tabulate'
    ],
    tests_require=[
        'nose',
        'coverage',
    ],
    entry_points={
        'console_scripts': [
            'pgcsv = pgcsv.cli:main'
        ]
    }
)
