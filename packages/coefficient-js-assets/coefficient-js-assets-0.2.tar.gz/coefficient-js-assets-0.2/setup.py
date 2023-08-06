from setuptools import find_packages, setup

setup(
    name='coefficient-js-assets',
    version='0.2',
    license='MIT',
    author="John Sandall",
    author_email='contact@coefficient.ai',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['*.js', '*.css']},
    url='https://github.com/john-sandall/',
    keywords='js',
    install_requires=[
          '',
      ],

)
