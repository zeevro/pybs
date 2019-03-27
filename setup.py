from setuptools import setup, find_packages


setup(
    name='pybs',
    version='0.0.1',
    url='https://github.com/zeevro/pybs',
    download_url='https://github.com/zeevro/pybs/archive/master.zip',
    license='None',
    author='Zeev Rotshtein',
    author_email='zeevro@gmail.com',
    keywords=['blinkstick'],
    zip_safe=True,
    packages=find_packages(),
    python_requires='',
    install_requires=[
        'hidapi',
        'webcolors'
    ],
    entry_points={
        'console_scripts': [
            'blinkstick = pybs.blinkstick:main'
         ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha'
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: Python 3',
        'Topic :: System :: Hardware',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
