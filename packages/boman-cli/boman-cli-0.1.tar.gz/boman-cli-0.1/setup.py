from setuptools import setup

setup(
    name='boman-cli',
    version='0.01',    
    description='CLI tool for boman.ai',
    url='https://boman.ai',
    author='Sumeru Software Solutions',
    author_email='sumerunordiks@gmail.com',
    license='BSD 2-clause',
    packages=['bomancli'],
    entry_points = {
        'console_scripts': ['boman-cli=bomancli.main:default'],
    },
    install_requires=['docker',
                      'requests',
                      'pyyaml',
                      'coloredlogs'                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)