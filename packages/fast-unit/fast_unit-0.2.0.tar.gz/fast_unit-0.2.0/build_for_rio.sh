rustup target add arm-unknown-linux-gnueabi

export PYO3_CROSS_PYTHON_VERSION=3.10
export PYO3_CROSS_LIB_DIR="lib/lib/"

maturin publish --target=arm-unknown-linux-gnueabi --rustc-extra-args="-C linker=arm-linux-gnueabi-gcc"