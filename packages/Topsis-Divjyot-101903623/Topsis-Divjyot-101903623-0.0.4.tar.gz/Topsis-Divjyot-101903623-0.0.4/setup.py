from setuptools import setup


def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name='Topsis-Divjyot-101903623',
    version='0.0.4',
    license='MIT',
    description='This is a Python Package implementing TOPSIS used for multi-criteria decision analysis method',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='Divjyot Singh',
    author_email='divjyot225@gmail.com',
    keywords=['topsis', 'mcda'],
    install_requires=[
        'numpy',
        'pandas',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
    ],
)