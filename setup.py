import setuptools

setuptools.setup(
            name="pyintruder",
            description="A python program for brute forcing; useful for testing for XSS vulnerabilities by checking for unblocked tags an attributes.",
            version="1.0.6",
            packages=setuptools.find_namespace_packages(where="src"),
            include_package_data=True,
            python_requires='>=3.8',
            install_requires=["aiohttp","importlib_resources","brotli"],
            url="https://github.com/Lukerd-29-00/pyintruder",
            package_dir={"": "src"}
        )