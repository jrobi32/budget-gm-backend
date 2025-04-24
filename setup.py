from setuptools import setup, find_packages

setup(
    name="budget-gm-backend",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-cors',
        'pandas',
        'numpy',
        'python-dotenv',
        'gevent',
        'gunicorn'
    ],
) 