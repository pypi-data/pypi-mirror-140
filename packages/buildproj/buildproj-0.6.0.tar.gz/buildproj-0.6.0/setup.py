from setuptools import setup

setup(name='buildproj',
      version='0.6.0',
      description='Alternative to make',
      url='http://github.com/Ehnryu/build',
      author='Ehnryu/Sakurai07',
      author_email='blzzardst0rm@gmail.com',
      license='MIT',
      packages=['buildproj'],
      entry_points={
        'console_scripts': [
            'build = buildproj.cli:launch',
        ],
    },
    install_requires=[
        'tqdm',
        ],
    keywords=['build', 'make',"project"],
    classifiers=["Programming Language :: Python :: 3"],
      zip_safe=False)