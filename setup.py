from setuptools import setup

setup(
    name='taskSwitching',
    version='0.1.0',
    description='Python version of the psychophysics Task Switching Paradigm',
    long_description='Designed for compatibility with fMRI scanner button boxes.',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3.6',
      'Topic :: Psychophysics :: Task switching',
    ],
    keywords='task switching psychophysics fMRI psychology cognitive neuroscience',
    url='http://github.com/daniellekurtin/task_switching_paradigm',
    author=['Matt Jaquiery', 'Danielle Kurtin'],
    author_email='danielle.kurtin18@imperial.ac.uk',
    license='MIT',
    packages=['taskSwitching'],
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    zip_safe=False
)
