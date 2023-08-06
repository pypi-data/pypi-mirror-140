from setuptools import setup
from setuptools_rust import RustExtension, Binding

setup(
    name="hash-ring-rs",
    version="0.1.4",
    rust_extensions=[RustExtension("hash_ring_rs", binding=Binding.PyO3)],
    zip_safe=False
)
