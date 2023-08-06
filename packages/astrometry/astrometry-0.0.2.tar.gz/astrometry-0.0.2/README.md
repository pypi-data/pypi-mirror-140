# astrometry
A Python wrapper for core Astrometry.net functions

```sh
rm -rf astrometry.egg-info; rm -rf astrometry_extension.cpython-39-darwin.so; rm -rf build; python3 setup.py develop
```

Pre-build
```sh
python3 prebuild.py
```

```sh
clang-format -i astrometry_extension/astrometry_extension.c; CC="ccache clang" python3 setup.py develop --disable-lto;
```