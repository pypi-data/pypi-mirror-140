from distutils.core import setup
setup(
    # How you named your package folder (MyLib)
    name='Topsis_Akshat_101917196',
    packages=['Topsis_Akshat_101917196'],   # Chose the same as "name"
    version='0.1',      # Start with a small number and increase it with every change you make
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    # Give a short description about your library
    description='A pip library for TOPSIS',
    author='Akshat Malik',                   # Type in your name
    author_email='amalik4_be19@thapar.edu',      # Type in your E-Mail
    # Provide either the link to your github or to your website
    url='https://github.com/AkshatMalikp/TOPSIS',
    # I explain this later on
    download_url='https://github.com/AkshatMalikp/TOPSIS/archive/refs/heads/main.zip',
    # Keywords that define your package best
    keywords=['topsis', 'Rank', 'Best', 'Model'],
    install_requires=[            # I get to this in a second
        'numpy',
        'pandas',
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
    ],
)