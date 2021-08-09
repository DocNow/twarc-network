import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name='twarc-network',
    version='0.0.6',
    url='https://github.com/docnow/twarc-network',
    author='Ed Summers',
    author_email='ehs@pobox.com',
    packages=['twarc_network'],
    description='Generate network visualizations for Twitter data',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.3',
    install_requires=['twarc', 'networkx', 'pydot'],
    setup_data={"twarc_network": ["twarc_network/index.html"]},
    package_data={"twarc_network": ["index.html"]},
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points='''
        [twarc.plugins]
        network=twarc_network:network
    '''
)
