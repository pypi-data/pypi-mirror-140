from distutils.core import setup
setup(
    name='Topsis-Akshat-102083028',
    packages=['Topsis-Akshat-102083028'],
    version='0.0.1',
    license='MIT',
    description='Multicriteria decision making using topsis analysis',
    author='Akshat Thakur',                   # Type in your name
    author_email='athakur3_be19@thapar.edu',      # Type in your E-Mail
    url='https://github.com/akshat00001/Topsis-Akshat-102083028',
    # I explain this later on
    download_url='https://github.com/akshat00001/Topsis-Akshat-102083028/archive/refs/tags/0.1.tar.gz',
    # Keywords that define your package best
    keywords=['MULTIDIMENSIONAL', 'TOPSIS'],
    install_requires=[            # I get to this in a second
        'numpy',
        'pandas',
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
