from distutils.core import setup
setup(
    name='generate_face',         # How you named your package folder (MyLib)
    packages=['generate_face'],   # Chose the same as "name"
    version='3.0',      # Start with a small number and increase it with every change you make
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    # Give a short description about your library
    description='Automatically download face from www.thispersondoesnotexist.com',
    author='edbert khovey',                   # Type in your name
    author_email='edbert.khovey@binus.ac.id',      # Type in your E-Mail
    # Provide either the link to your github or to your website
    url='https://github.com/evoreign/generate_face',
    # I explain this later on
    download_url='https://github.com/evoreign/generate_face/archive/refs/tags/3.0.tar.gz',
    # Keywords that define your package best
    keywords=['face', 'library', 'data science'],
    install_requires=[            # I get to this in a second
        'requests',
    ],
)
