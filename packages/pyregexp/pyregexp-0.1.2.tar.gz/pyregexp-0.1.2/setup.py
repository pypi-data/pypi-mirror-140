from distutils.core import setup

setup(
    name='pyregexp',
    packages=['pyregexp'],
    version='0.1.2',
    license='MIT',
    description='Simple regex library',
    author='Lorenzo Felletti',
    url='https://github.com/lorenzofelletti/pyregex_lib',
    download_url='https://github.com/lorenzofelletti/pyregex_lib/archive/v0.1.2.tar.gz',
    keywords=['Regex', 'RegExp', 'Engine'],
    install_requires=[            # I get to this in a second
        'numpy',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
