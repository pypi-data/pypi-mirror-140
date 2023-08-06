from setuptools import setup


setup(
    name='jupyterlite-sphinx',
    version='0.2.0',
    package_dir={'': 'src'},
    py_modules=['jupyterlite_sphinx'],
    python_requires='>=3.7',
    install_requires=[
        'docutils',
        'jupyterlite',
        'sphinx>=1.8',
    ],
    author='Martin Renou',
    author_email='martin.renou@gmail.com',
    description='Sphinx extension for deploying JupyterLite',
    license='MIT',
    zip_safe=True,
)
