from setuptools import setup

"""The setup script.
# 作者-上海悠悠 QQ交流群:717225969
# blog地址 https://www.cnblogs.com/yoyoketang/
"""

setup(
    name='pytest-change-demo',
    url='https://github.com/simayang/test2/pytest-change-demo',
    version='1.0',
    author="yoyo",
    author_email='283340479@qq.com',
    description='turn . into √，turn F into x',
    long_description='print result on terminal turn . into √，turn F into x using hook',
    classifiers=[
        'Framework :: Pytest',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 3.6',
    ],
    license='proprietary',
    py_modules=['pytest_change_demo'],
    keywords=[
        'pytest', 'py.test', 'pytest-change-demo',
    ],

    install_requires=[
        'pytest'
    ],
    entry_points={
        'pytest11': [
            'change-report = pytest_change_demo',
        ]
    }
)