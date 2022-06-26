from setuptools import setup


setup(
    name='ebookmeta',
    version='1.1.4',
    author='Dmitrii Korpushov',
    author_email='dnkorpushov@gmail.com',
    packages=['ebookmeta'],
    url='https://github.com/dnkorpushov/ebookmeta',
    license='MIT',
    description='Read/write ebook metadata for fb2, epub2 and epub3 files',
    keywords=['ebook', 'epub', 'metadata', 'fb2'],
    classifiers=[
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    install_requires=['lxml']
)
