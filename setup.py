from setuptools import setup, find_packages


with open('requirements.txt') as f:
    required = [line.strip() for line in f]


setup(
    name='ThemeSearcher',
    version="1.0",
    license="MIT License",
    url="https://github.com/olegborzov/ThemeSearcher",

    description="Сервис для определения тем по запросу пользователя",
    long_description=open('README.md').read(),

    author="Олег Борзов",
    author_email="mail@olegborzov.ru",

    packages=find_packages(exclude=('tests',)),
    python_requires=">=3.7.0",
    install_requires=required,
    test_suite="tests",
    entry_points={
        "console_scripts": [
            "serve = server:run_server"
        ]
    }
)
