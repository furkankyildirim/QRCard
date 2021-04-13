from setuptools import setup

setup(
    name="QRCard",
    version="1.0.0",
    maintainer="Furkan K. Yıldırım",
    maintainer_email="furkan.k.yildirim@gmail.com",
    packages=['QRCard'],
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask"]
)