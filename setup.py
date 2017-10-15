from setuptools import setup

setup(name='pyAdsWebService',
      version='0.1.0',
      description='Python wrapper to read and write value to a Twincat PLC through a an ADS Web Service',
      #url='http://github.com/storborg/funniest',
      author='G. Robichaud',
      author_email='robichaud.g@gmail.com',
      license='MIT',
      packages=['pyAdsWebService'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)
