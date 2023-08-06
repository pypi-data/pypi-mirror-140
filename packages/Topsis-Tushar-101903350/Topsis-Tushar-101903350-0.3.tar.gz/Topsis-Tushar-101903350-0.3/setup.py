from distutils.core import setup
setup(
    # How you named your package folder (MyLib)
    name='Topsis-Tushar-101903350',
    packages=['Topsis-Tushar-101903350'],   # Chose the same as "name"
    version='0.3',      # Start with a small number and increase it with every change you make
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    # Give a short description about your library
    description='Technique for Order Preference by Similarity to Ideal Solution (TOPSIS) originated in the 1980s as a multi-criteria decision making method. TOPSIS chooses the alternative of shortest Euclidean distance from the ideal solution, and greatest distance from the negative-ideal solution.',
    author='Tushar Pruthi',                   # Type in your name
    author_email='tpruthi_be19@thapar.edu',      # Type in your E-Mail
    # Provide either the link to your github or to your website
    url='https://github.com/Tush1810/Topsis-Tushar-101903350',
    # I explain this later on
    download_url='https://github.com/Tush1810/Topsis-Tushar-101903350/archive/refs/tags/v_03.tar.gz',
    # Keywords that define your package best
    keywords=['Python', 'Topsis', '101903350'],
    install_requires=[            # I get to this in a second
        'numpy',
        'pandas'
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        # Define that your audience are developers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
)
