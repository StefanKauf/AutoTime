# AutoTime
Automatic Time Managment

SimpleGui is a Python Tool to interact with SAP and Project Report Tools.


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install SimpleGui.

```powershell
# Load Requirements
python -m pip install -r requirements.txt
```

## Usage

```python 3.12

# Save Requirements
pip freeze > requirements.txt


# Convert SAPGui.ui  to Python File
pyuic5 SAPGui.ui -o SAPGui.py

# Create Exe
pyinstaller --onefile --optimize 2 --clean SimpleGui.py

```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
