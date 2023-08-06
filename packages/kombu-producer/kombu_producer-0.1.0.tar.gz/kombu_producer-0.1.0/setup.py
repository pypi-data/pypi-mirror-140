from setuptools import setup
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
  name='kombu_producer',
  packages=['kombu_producer'],
  version='0.1.0',
  license='MIT',
  description='Python library that implements a simple Kombu producer',
  long_description=README,
  long_description_content_type="text/markdown",
  author='Deepanshu Gupta',
  author_email='deepanshu71095@gmail.com',
  url='https://github.com/Deepanshu07/kombu_producer',
  download_url='https://github.com/Deepanshu07/kombu_producer/archive/refs/tags/v0.1.0.tar.gz',
  keywords=['Kombu', 'Kombu-producer'],
  install_requires=[
          'amqp',
          'kombu',
          'vine',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
  ],
)