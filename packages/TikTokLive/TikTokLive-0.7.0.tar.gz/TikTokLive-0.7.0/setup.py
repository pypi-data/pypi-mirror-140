import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TikTokLive",
    packages=setuptools.find_packages(),
    version="0.7.0",
    license="MIT",
    description="TikTok Live Connection Client (Unofficial)",
    author="Isaac Kogan",
    author_email="info@isaackogan.com",
    url="https://github.com/isaackogan/TikTok-Live-Connector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url="https://github.com/isaackogan/TikTokLive/archive/refs/tags/v0.7.0.zip",
    keywords=["tiktok", "tiktok live", "python3", "api", "unofficial"],
    install_requires=[
        "aiohttp>=3.8",  # Make requests
        "protobuf3-to-dict>=0.1.5",  # Convert Protobuf to Dict
        "protobuf>=3.19.4",  # Decode Protobuf Messages
        "pyee>=9.0.4",  # Event Emitter
        "dacite>=1.6.0"  # Requests
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ]
)
