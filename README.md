# AesCrypt - File Encryption/Decryption Utility

A simple Python utility for encrypting and decrypting files using AES (Advanced Encryption Standard) encryption algorithm.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Interactive Mode](#interactive-mode)
  - [Programmatic Usage](#programmatic-usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)

## Overview

AesCrypt is a lightweight file encryption tool that provides secure file encryption and decryption capabilities using the AES algorithm. The utility supports both interactive command-line usage and programmatic integration.

## Features

- **AES Encryption**: Secure file encryption using industry-standard AES algorithm
- **Interactive Interface**: User-friendly command-line interface with prompts
- **Flexible Input**: Supports various file types and custom output naming
- **Bilingual Support**: Interface supports Ukrainian language prompts
- **Error Handling**: Comprehensive error handling with informative messages
- **Lightweight**: Minimal dependencies and simple implementation

## Prerequisites

- Python 3.6 or higher
- pyAesCrypt library

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd AesCrypt
   ```

2. **Install dependencies:**
   ```bash
   pip install pyAesCrypt
   ```

3. **Make the script executable (optional):**
   ```bash
   chmod +x AesCrypt.py
   ```

## Usage

### Interactive Mode

Run the script directly to use the interactive mode:

```bash
python AesCrypt.py
```

The program will prompt you for:
1. **Action**: Choose to encrypt (`E`) or decrypt (`D`)
2. **File path**: Path to the input file
3. **Password**: Password for encryption/decryption
4. **Output file**: Name/path for the output file

### Programmatic Usage

You can also import and use the functions in your own Python scripts:

```python
from AesCrypt import cryptFile, get_data_from_user
import pyAesCrypt

# Use the interactive function
data = get_data_from_user()
cryptFile(data["action"], data["pass"], data["path"], data["output"])

# Or call cryptFile directly
cryptFile("e", "your_password", "input.txt", "encrypted.txt.aes")
```

## API Reference

### Functions

#### `get_data_from_user() -> dict`

Interactively collects user input for encryption/decryption operations.

**Returns:**
- `dict`: Dictionary containing user inputs with keys:
  - `action` (str): "e" for encrypt, "d" for decrypt
  - `pass` (str): Password for the operation
  - `path` (str): Path to input file
  - `output` (str): Output file name/path

**Example:**
```python
user_data = get_data_from_user()
# Returns: {"action": "e", "pass": "mypassword", "path": "data.txt", "output": "data.txt.aes"}
```

#### `cryptFile(action: str, password: str, file: str, output: str) -> None`

Performs file encryption or decryption based on the specified action.

**Parameters:**
- `action` (str): Operation type - "e" for encrypt, "d" for decrypt
- `password` (str): Password for encryption/decryption
- `file` (str): Path to the input file
- `output` (str): Path for the output file

**Raises:**
- `ValueError`: When password is incorrect or file operations fail
- `FileNotFoundError`: When input file doesn't exist

**Example:**
```python
# Encrypt a file
cryptFile("e", "mypassword", "document.pdf", "document.pdf.aes")

# Decrypt a file
cryptFile("d", "mypassword", "document.pdf.aes", "document_decrypted.pdf")
```

#### `main()`

Main entry point that orchestrates the interactive encryption/decryption process.

**Functionality:**
- Calls `get_data_from_user()` to collect input
- Executes `cryptFile()` with collected data
- Handles and displays errors appropriately

## Examples

### Example 1: Encrypt a Text File

```python
import pyAesCrypt
from AesCrypt import cryptFile

# Encrypt a text file
try:
    cryptFile("e", "secure_password123", "secret_notes.txt", "secret_notes.txt.aes")
    print("File encrypted successfully!")
except ValueError as e:
    print(f"Encryption failed: {e}")
```

### Example 2: Decrypt a File

```python
import pyAesCrypt
from AesCrypt import cryptFile

# Decrypt a file
try:
    cryptFile("d", "secure_password123", "secret_notes.txt.aes", "decrypted_notes.txt")
    print("File decrypted successfully!")
except ValueError as e:
    print(f"Decryption failed: {e}")
```

### Example 3: Batch Processing

```python
import os
import pyAesCrypt
from AesCrypt import cryptFile

def encrypt_directory(directory_path, password, extension=".aes"):
    """Encrypt all files in a directory"""
    for filename in os.listdir(directory_path):
        if not filename.endswith(extension):
            file_path = os.path.join(directory_path, filename)
            output_path = file_path + extension
            try:
                cryptFile("e", password, file_path, output_path)
                print(f"Encrypted: {filename}")
            except ValueError as e:
                print(f"Failed to encrypt {filename}: {e}")

# Usage
encrypt_directory("/path/to/files", "batch_password")
```

### Example 4: Interactive Usage Script

```python
import pyAesCrypt
from AesCrypt import main

if __name__ == "__main__":
    print("=== AesCrypt File Security Tool ===")
    print("This tool will help you encrypt or decrypt files securely.")
    print("Please follow the prompts below:\n")
    
    main()
```

## Error Handling

The utility includes comprehensive error handling:

### Common Errors

- **Incorrect Password**: 
  ```
  [-] bad decrypt (file is corrupted or password is incorrect)
  ```

- **File Not Found**:
  ```
  [-] [Errno 2] No such file or directory: 'filename.txt'
  ```

- **Permission Denied**:
  ```
  [-] [Errno 13] Permission denied: 'protected_file.txt'
  ```

### Best Practices

1. **Always verify file paths** before running operations
2. **Use strong passwords** with mixed characters, numbers, and symbols
3. **Keep backups** of important files before encryption
4. **Store passwords securely** - the utility doesn't store them

## Security Considerations

### Password Security
- Use strong, unique passwords for each file
- Avoid using easily guessable passwords
- Consider using a password manager
- Never hardcode passwords in scripts

### File Security
- Securely delete original files after encryption if needed
- Store encrypted files and passwords separately
- Regular backup of encrypted files
- Be aware that file metadata might still be visible

### Implementation Notes
- Uses pyAesCrypt library which implements AES-256-CBC
- Password-based key derivation using PBKDF2
- No password recovery mechanism - lost passwords mean lost data

## Dependencies

- **pyAesCrypt**: AES encryption library for Python
  ```bash
  pip install pyAesCrypt
  ```

## File Structure

```
AesCrypt/
├── AesCrypt.py          # Main application file
└── README.md            # This documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## License

This project is open source. Please check the repository for license details.

## Support

For issues, questions, or contributions, please refer to the project repository or create an issue in the issue tracker.

---

**Note**: Always ensure you have backups of important files before using encryption tools. Lost passwords cannot be recovered and will result in permanent data loss.