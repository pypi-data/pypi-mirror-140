# Fast Unit - Rust Unit Management for Python

Originally created as a faster version of [Unum](https://pypi.org/project/Unum/) 
for use in Python-based FRC robot code.

## Building and Installing for Local Machine

```shell
maturin build --release  # This will generate wheels and put a native library in ./fast_unit/
pip install .  # Installs to your python interpreter
```

## Cross Compilation for RoboRIO (WIP)

### Getting Required Files

In order to compile for RoboRIO, you need to copy the contents of `/usr/local/lib` and
update the `RIO_ROOT` to reflect where you copied them. This is assuming you have already
installed python on your RIO using [RobotPy](https://robotpy.readthedocs.io/en/stable/).

This is the command I used to accomplish this:

```shell
scp lvuser@roboRIO-XXXX-FRC.local:/usr/local/lib ./RIO_ROOT/usr/local/lib
```

### Installing ARM Linker

Rust needs an arm linker to compile arm binaries, which can be installed fairly easily. 
On debian, run the following:

```shell
sudo apt install gcc-arm-linux-gnueabi
```

### Building

Once you have the required tools, running the script below should compile and build
the wheels.

```shell
# Add RIO's target triple
rustup target add arm-unknown-linux-gnueabi

# Set cross-compilation environment variables
export PYO3_CROSS_PYTHON_VERSION=3.10
export PYO3_CROSS_LIB_DIR="RIO_ROOT/usr/local/lib"

# Build wheels for RIO
maturin build --target=arm-unknown-linux-gnueabi --rustc-extra-args="-C linker=arm-linux-gnueabi-gcc"
```