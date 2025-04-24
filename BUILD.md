## opencc_jieba_pyo3

### Module folder
create module folder in project root `./opencc_jieba_pyo3` same name as sated in cargo.toml:

```toml
[lib]
name = "opencc_pyo3"
```
create pyproject.toml in project root
```toml
[build-system]
requires = ["maturin>=1.7,<2.0"]
build-backend = "maturin"

[project]
name = "opencc_jieba_pyo3"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Rust",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
]
dynamic = ["version"]
[tool.maturin]
features = ["pyo3/extension-module"]
```
### Build pyd
prepare files in module folder:
```
__init__.py
opencc_jieba_pyo3.pyi
```

- prepare `.venv` if needed
- Create pyd to opencc_jieba_pyo3 module folder, need `.venv` env, delete any existing pyd file in the folder.
    ```bash
    maturin develop -r
    ``` 
### Build wheels package
- Exit `.venv`, back to System Python
    ```bash
    maturin build -r
    ```
- Install wheels using **pip**
    ```bash
    pip install ./target/wheels/opencc_jieba_pyo3-0.4.0-cp312-cp312-win_amd64.whl --force-reinstall
    ```
