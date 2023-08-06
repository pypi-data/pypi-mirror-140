from setuptools import find_packages, setup


NAME = "portant-mailing"
DESCRIPTION = "a Django mailing app for Portant shop"
AUTHOR = "Vedran Vojvoda"
AUTHOR_EMAIL = "vedran@pinkdroids.com"
URL = "https://github.com/portant-shop/mailing"
LONG_DESCRIPTION = """
============
Django WSPay
============

This django app provides simple support for payments using WSPay gateway.
"""

tests_require = [
    "pytest",
    "pytest-django"
]

setup(
    name=NAME,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    version="1.0.3",
    license="MIT",
    url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
    ],
    include_package_data=True,
    install_requires=[
        "celery>=5.2.3",
        "Django>=3.0",
        "redis>=4.1.4",
        "django-appconf"
    ],
    extras_require={
        "testing": tests_require,
    },
    zip_safe=False,
)
