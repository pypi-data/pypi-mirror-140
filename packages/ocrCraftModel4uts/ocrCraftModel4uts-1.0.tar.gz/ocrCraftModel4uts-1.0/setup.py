from setuptools import setup, find_packages
setup(
    name='ocrCraftModel4uts',
    version='1.0',
    author='Jinzhe Wang',
    description='Deploying OCR text detection model files for uitestrunner-syberos',
    author_email='wangjinzhe@syberos.com',
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={
        "ocrCraftModel4uts": ["data/*"]
    },
    python_requires=">=3.8, <4"
)