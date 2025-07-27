"""
AesCrypt - File Encryption/Decryption Utility

A simple Python utility for encrypting and decrypting files using AES 
(Advanced Encryption Standard) encryption algorithm via the pyAesCrypt library.

This module provides both interactive command-line functionality and 
programmatic access to file encryption/decryption operations.

Author: AesCrypt Project
License: Open Source
Dependencies: pyAesCrypt

Example:
    Interactive usage:
        $ python AesCrypt.py
    
    Programmatic usage:
        >>> from AesCrypt import cryptFile
        >>> cryptFile("e", "password", "input.txt", "output.txt.aes")
"""


def get_data_from_user() -> dict:
    """
    Interactively collects user input for encryption/decryption operations.
    
    This function prompts the user through a series of questions to gather
    all necessary information for file encryption or decryption, including
    the operation type, file paths, and password.
    
    The function includes input validation to ensure the user selects a
    valid operation type (encrypt or decrypt).
    
    Returns:
        dict: A dictionary containing user inputs with the following keys:
            - 'action' (str): "e" for encrypt, "d" for decrypt
            - 'pass' (str): Password for the encryption/decryption operation
            - 'path' (str): Path to the input file
            - 'output' (str): Path/name for the output file
    
    Example:
        >>> data = get_data_from_user()
        Зашифрувати(encrypt) чи розшифрувати(decrypt)
        E or D: e
        Введіть назву або шлях до файла(data.txt / data.txt.aes): document.txt
        Введіть пароль для файла: mypassword
        Введіть назву вихідного файла(data.txt / data.txt.aes): document.txt.aes
        >>> print(data)
        {'action': 'e', 'pass': 'mypassword', 'path': 'document.txt', 'output': 'document.txt.aes'}
    """
    print("Зашифрувати(encrypt) чи розшифрувати(decrypt)")
    action = input("E or D: ").strip().lower()
    
    # Input validation loop for action selection
    while action not in ["e", "d", "encrypt", "decrypt"]:
        action = input("E or D: ").strip().lower()
    
    # Normalize action to single character
    if action in ["e", "encrypt"]:
        action = "e"
    else:
        action = "d"

    # Collect file paths and password
    path_to_file = input("Введіть назву або шлях до файла(data.txt / data.txt.aes): ")
    password = input("Введіть пароль для файла: ")
    output_file_name = input("Введіть назву вихідного файла(data.txt / data.txt.aes): ")

    return {"action": action, "pass": password,
            "path": path_to_file, "output": output_file_name}


def cryptFile(action: str, password: str, file: str, output: str) -> None:
    """
    Performs file encryption or decryption using AES algorithm.
    
    This function serves as a wrapper around the pyAesCrypt library functions,
    providing a unified interface for both encryption and decryption operations.
    
    Args:
        action (str): The operation to perform:
            - "e" or "encrypt": Encrypt the file
            - "d" or "decrypt": Decrypt the file
        password (str): Password for encryption/decryption. Should be strong
            and unique for security purposes.
        file (str): Path to the input file to be processed. File must exist
            and be readable.
        output (str): Path for the output file. Directory must be writable.
    
    Returns:
        None: This function doesn't return a value but creates the output file.
    
    Raises:
        ValueError: If the password is incorrect during decryption, or if
            there are issues with file processing.
        FileNotFoundError: If the input file doesn't exist.
        PermissionError: If there are insufficient permissions to read the
            input file or write the output file.
    
    Example:
        >>> # Encrypt a file
        >>> cryptFile("e", "secure_password", "document.pdf", "document.pdf.aes")
        >>> 
        >>> # Decrypt a file
        >>> cryptFile("d", "secure_password", "document.pdf.aes", "document_restored.pdf")
    
    Note:
        - The pyAesCrypt library uses AES-256-CBC encryption
        - Password-based key derivation is performed using PBKDF2
        - There is no password recovery - lost passwords mean lost data
    """
    if action == 'e':
        # Encrypt the file using AES encryption
        pyAesCrypt.encryptFile(file, output, password)
    else:
        # Decrypt the file using AES decryption
        pyAesCrypt.decryptFile(file, output, password)


def main():
    """
    Main entry point for the interactive AesCrypt utility.
    
    This function orchestrates the complete encryption/decryption workflow:
    1. Collects user input via get_data_from_user()
    2. Performs the requested operation via cryptFile()
    3. Handles any errors that may occur during processing
    4. Provides user feedback on operation completion
    
    The function includes comprehensive error handling to catch and display
    meaningful error messages for common issues like incorrect passwords,
    missing files, or permission problems.
    
    Returns:
        None: This function handles all user interaction and doesn't return a value.
    
    Example:
        >>> main()
        Зашифрувати(encrypt) чи розшифрувати(decrypt)
        E or D: e
        Введіть назву або шлях до файла(data.txt / data.txt.aes): test.txt
        Введіть пароль для файла: mypassword
        Введіть назву вихідного файла(data.txt / data.txt.aes): test.txt.aes
        Finish!
    
    Error Handling:
        - Catches ValueError for password/corruption issues
        - Displays user-friendly error messages with [-] prefix
        - Continues execution after errors (doesn't crash)
    """
    # Collect user input for the operation
    data = get_data_from_user()

    try:
        # Perform the encryption/decryption operation
        cryptFile(action=data.get("action"),
                  password=data.get("pass"),
                  file=data.get("path"),
                  output=data.get("output"))
        print("Finish!")

    except ValueError as error:
        # Handle common errors like incorrect passwords or file issues
        print(f'[-] {error}')


if __name__ == '__main__':
    # Import pyAesCrypt library when running as main module
    # This allows the module to be imported without requiring pyAesCrypt
    # to be installed if only using it programmatically
    import pyAesCrypt
    
    # Start the interactive encryption/decryption process
    main()
