"""Setup configuration for gakumonnosusume package"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gakumonnosusume",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="福沢諭吉風テキストジェネレーター - Fukuzawa Yukichi-style text generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gakumonnosusume",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-openai>=0.0.5",
        "langchain-anthropic>=0.1.0",
        "chromadb>=0.4.22",
        "sentence-transformers>=2.2.2",
        "click>=8.1.7",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
        "tiktoken>=0.5.2",
    ],
    entry_points={
        "console_scripts": [
            "gakumon=src.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["prompts/*.md"],
    },
)
