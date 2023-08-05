from setuptools import setup, find_packages
setup(
    name='ocrLangModel4uts',
    version='1.0',
    author='Jinzhe Wang',
    description='Deploying OCR lang model files for uitestrunner-syberos',
    author_email='wangjinzhe@syberos.com',
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={
        "ocrLangModel4uts": ["data/*"]
    },
    python_requires=">=3.8, <4"
)