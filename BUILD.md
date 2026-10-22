# Building opencc-jieba-pyo3

This guide covers building, installing, testing, and developing **opencc-jieba-pyo3**, the Python bindings for the
Rust-based OpenCC + Jieba converter.

For everyday installation, prefer a published wheel from PyPI:

```sh
python -m pip install opencc-jieba-pyo3
```

A compatible prebuilt wheel does not require Rust on the user's machine. Source installations and local builds do.

## Requirements

- **CPython 3.8 or newer** (as declared in `pyproject.toml`).
- A working **Rust toolchain** (`rustc` and `cargo`) for source builds; install via [rustup](https://rustup.rs/).
- **maturin** for direct development and wheel-building commands.
- Platform-specific C/C++ build and linker tools: for example, MSVC Build Tools on Windows, Xcode Command Line Tools on
  macOS, or a compiler/linker toolchain on Linux.
- **Git** only when cloning the repository or installing from a Git URL.

Check the environment:

```sh
python --version
rustc --version
cargo --version
```

Use the Python interpreter associated with the environment in which you intend to install the package. On Windows,
`py -3.13` or another installed interpreter can be used in place of `python`.

## Repository layout and build configuration

The repository already contains the necessary build files; **do not create a new module directory or `pyproject.toml`**.

```text
opencc_jieba_pyo3/
├── Cargo.toml
├── pyproject.toml
├── src/
│   └── lib.rs                 # PyO3 native bindings
└── opencc_jieba_pyo3/
    ├── __init__.py            # High-level Python API
    ├── __main__.py            # CLI entry point
    ├── opencc_jieba_pyo3.pyi  # Type declarations
    └── py.typed               # PEP 561 typing marker
```

The Rust library is configured as a `cdylib` named `opencc_jieba_pyo3`. `pyproject.toml` uses maturin as the PEP 517
build backend and derives the package version from Cargo metadata.

The project enables PyO3's **`abi3-py38`** feature. Compatible wheels are tagged `cp38-abi3`, allowing one
platform-specific wheel to work across supported CPython versions, subject to other compatibility constraints. For
example:

```text
opencc_jieba_pyo3-0.8.0-cp38-abi3-win_amd64.whl
```

The example version is illustrative; the actual version comes from `Cargo.toml`.

**Important:** The repository defines an `extension-module` Cargo feature but intentionally does not enable it by
default. Use it for extension builds when appropriate; leave it disabled for ordinary `cargo test` runs. This avoids
Python linking issues for Rust test executables, particularly on Linux.

## Clone and prepare a development environment

```sh
git clone https://github.com/laisuk/opencc_jieba_pyo3.git
cd opencc_jieba_pyo3
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```sh
source .venv/bin/activate
```

Install the build frontend:

```sh
python -m pip install --upgrade pip maturin
```

If PowerShell activation is restricted, invoke `.venv\Scripts\python.exe` directly instead of activating the
environment.

## Development build (editable installation)

With the intended virtual environment active, run:

```sh
maturin develop --release
```

This compiles the Rust extension and installs it into the active environment for local development. `-r` is shorthand
for `--release`.

For a faster, unoptimized development build:

```sh
maturin develop
```

You do **not** need to delete an existing `.pyd`/`.so` extension before every rebuild. You also do not need to exit the
virtual environment to build a wheel.

Verify the installation:

```sh
python -c "from opencc_jieba_pyo3 import OpenCC; print(OpenCC('s2t').convert('汉字', False))"
```

Expected output:

```text
漢字
```

After changing Rust/PyO3 code, rerun `maturin develop --release`. Pure Python changes may not require recompilation,
depending on how the development installation is linked or copied.

## Build a distributable wheel

From the repository root:

```sh
maturin build --release
```

The resulting wheel is written to `target/wheels/`. Its exact filename depends on the package version, ABI, operating
system, and architecture. Examples of platform tags include `win_amd64`, `manylinux_*_x86_64`, and `macosx_*_arm64`.

To build for a specific installed interpreter:

```sh
maturin build --release --interpreter python
```

Install the **actual generated wheel filename**, for example:

```sh
python -m pip install --force-reinstall ./target/wheels/opencc_jieba_pyo3-0.8.0-cp38-abi3-win_amd64.whl
```

Do not copy this example filename blindly: inspect `target/wheels/` first. An `abi3` wheel is not the old `cp312-cp312`
interpreter-specific wheel.

For distributing Linux wheels to other machines, check the wheel's compatibility tags and use an appropriate
manylinux/musllinux build environment or an audited repair workflow where required. A wheel built on a developer machine
is not automatically portable to all Linux systems.

## Install from a source distribution (sdist)

A Python source distribution (`.tar.gz`) can be installed with pip. Because the native extension must be compiled, a
Rust toolchain and native build tools are required.

```sh
python -m pip install ./opencc_jieba_pyo3-0.8.0.tar.gz
```

To build an sdist locally:

```sh
maturin sdist
```

Install the archive actually produced under `target/wheels/` (the output location may depend on the maturin
invocation/version).

To force a source build from PyPI instead of using a prebuilt wheel:

```sh
python -m pip install --no-binary opencc-jieba-pyo3 opencc-jieba-pyo3
```

## Install directly from GitHub

Install the latest repository version (requires Git):

```sh
python -m pip install "git+https://github.com/laisuk/opencc_jieba_pyo3.git"
```

Install a specific branch, existing release tag, or commit:

```sh
python -m pip install "git+https://github.com/laisuk/opencc_jieba_pyo3.git@master"
python -m pip install "git+https://github.com/laisuk/opencc_jieba_pyo3.git@<existing-tag>"
python -m pip install "git+https://github.com/laisuk/opencc_jieba_pyo3.git@<commit-sha>"
```

Replace placeholders with real references. A branch may contain unreleased changes; pin a tag or commit for reproducible
builds.

### Install from a GitHub ZIP archive (no Git required)

Install a source snapshot of the default branch:

```sh
python -m pip install "https://github.com/laisuk/opencc_jieba_pyo3/archive/refs/heads/master.zip"
```

Or use an existing tag:

```sh
python -m pip install "https://github.com/laisuk/opencc_jieba_pyo3/archive/refs/tags/<existing-tag>.zip"
```

You may also download the archive first and install its local path. Unlike a prebuilt wheel, a Git checkout or GitHub
ZIP archive is source code: pip invokes maturin to compile the extension locally. GitHub-generated ZIP snapshots and
Python sdists are distinct archive formats.

## Run tests and checks

Run Rust unit tests **without enabling** the extension-module feature:

```sh
cargo test
```

Run Python tests against the installed extension, if the checkout includes a Python test suite:

```sh
python -m pip install pytest
python -m pytest
```

For Rust style and lint checks:

```sh
cargo fmt --all -- --check
cargo clippy --all-targets
```

Note that `cargo test` exercises Rust code; it does not replace a Python import/packaging smoke test. For a release
candidate, verify a freshly built wheel in a clean virtual environment.

## Troubleshooting

**`maturin: command not found`** — Install it in the active environment (`python -m pip install maturin`) and verify the
environment's scripts directory is on `PATH`.

**Python imports an old native extension** — Confirm which Python and package are being used:

```sh
python -c "import sys, opencc_jieba_pyo3; print(sys.executable); print(opencc_jieba_pyo3.__file__)"
```

Rebuild/reinstall in that environment if needed.

**Compiler or linker errors** — Check that the platform's native toolchain is installed and matches the Python
architecture (for example, 64-bit Python with the appropriate Windows build tools).

**Linux `cargo test` Python linker errors** — Ensure the `extension-module` feature is not enabled for standalone Rust
tests. It is intended for building the Python extension, not the test executable.

**Windows `WinError 1` during a pip source build** — Some RAM disks or unusual temporary filesystems may be incompatible
with pip's build operations. Point `TEMP` and `TMP` to a normal local filesystem and retry.

**Unexpected wheel tag** — Confirm `Cargo.toml` still enables PyO3 `abi3-py38` and inspect the actual wheel generated by
maturin. Do not assume every platform produces an identical wheel filename.

## Release checklist

1. Update the version and relevant dependency pins in `Cargo.toml` and update the changelog.
2. Confirm that the high-level Python API, native PyO3 methods, `.pyi` declarations, and README examples agree.
3. Run Rust tests and Python integration tests.
4. Build release wheels and verify a clean installation and import on each target platform.
5. Inspect wheel contents for `__init__.py`, the native extension, `.pyi`, `py.typed`, and the CLI module.
6. Verify the CLI entry point (`opencc-jieba-pyo3 --help`) and basic conversion behavior.
7. Publish only after checking release artifacts and their supported Python/platform tags.

For usage examples and package features, see [README.md](README.md).
