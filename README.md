## Library License Visualizer

### Example

See [HERE !](https://raw.githubusercontent.com/takkaO/LibraryLicenseVisualizer/refs/heads/main/example/license_list.mmd.svg)

### Getting started

> [!NOTE]
> Need Docker for translate mmd to svg.

```sh
python3 -m pip install -r requirements.txt
scan.bat ./example
python3 main.py
mmd2svg.bat ./output/license_list.mmd
start ./output/license_list.mmd.svg
```

### Note

- Using scancode-toolkit for identify licenses
- Only a few licenses have estimated relationships. Please edit license_relation.py to add or change them.
- The relationship between licenses is for reference only and is not guaranteed.