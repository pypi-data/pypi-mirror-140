FROM "quay.io/pypa/manylinux_2_24_x86_64"

WORKDIR /code
COPY . /code

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o rust.sh
RUN sh rust.sh -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustup override set nightly

RUN /opt/python/cp310-cp310/bin/pip install maturin
RUN /opt/python/cp310-cp310/bin/maturin publish --target=x86_64-unknown-linux-gnu --compatibility manylinux_2_24 \
    --username ethanmchapman --password dPuXufmV24Qg3j
