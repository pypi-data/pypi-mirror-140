from setuptools import setup, find_packages

setup(name='p1ufcg',
      version="0.1.5",
      description='P1 UFCG',
      url='http://github.com/daltonserey/p1',
      author='Dalton Serey',
      author_email='daltonserey@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      scripts=[],
      python_requires='>=3.6',
      install_requires=[
        'pyyaml>=5.4.1',
        'requests>=2.6.1',
        'cachecontrol[filecache]',
        'tst>=0.13.5'
      ],
      entry_points = {
        'console_scripts': [
            'p1=p1.commands:main',
        ]
      },
      zip_safe=False)
