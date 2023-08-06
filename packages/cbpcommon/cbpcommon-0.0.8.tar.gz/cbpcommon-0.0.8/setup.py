from setuptools import setup

setup(
    name='cbpcommon',
    version='0.0.8',
    url='https://github.com/Crypto-Bot-Platform/cbpcommon',
    license='MIT',
    author='Boris Tsekinovsky',
    author_email='t.boris@gmail.com',
    description='Common library for Crypto Bot Platform',
    packages=['.'],
    include_package_data=True,
    install_requires=["avro==1.11.0", "confluent_kafka==1.8.2", "setuptools>=60.9.0", "elasticsearch~=7.16.3",
                      "jsonpickle"],
)
