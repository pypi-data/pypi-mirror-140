from setuptools import find_packages, setup


if __name__ == '__main__':
    setup(

        # standard info
        name='ezazure',
        version='0.0.8',
        description='easy azure interface for uploading & downloading files',
        author='Mike Powell PhD',
        author_email='mike@lakeslegendaries.com',

        # longer info
        long_description=open('README.rst').read(),
        license=open('LICENSE').read(),

        # packages to include
        packages=find_packages(),

        # requirements
        install_requires=[
            'azure-storage-blob',
            'pyyaml',
        ],
        python_requires='>=3.7',
    )
