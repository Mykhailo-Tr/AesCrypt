#!/usr/bin/env python3
"""
Basic Usage Examples for AesCrypt

This file demonstrates common usage patterns for the AesCrypt utility,
including both interactive and programmatic approaches.
"""

import os
import sys
import tempfile

# Add the parent directory to the path so we can import AesCrypt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pyAesCrypt
    from AesCrypt import cryptFile, get_data_from_user, main
except ImportError as e:
    print(f"Error: {e}")
    print("Please install pyAesCrypt: pip install pyAesCrypt")
    sys.exit(1)


def example_1_basic_encryption():
    """Example 1: Basic file encryption and decryption"""
    print("=== Example 1: Basic Encryption/Decryption ===")
    
    # Create a temporary file with some content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write("This is secret content that needs to be encrypted!")
        temp_filename = temp_file.name
    
    try:
        password = "my_secure_password_123"
        encrypted_filename = temp_filename + ".aes"
        decrypted_filename = temp_filename + ".decrypted"
        
        print(f"Original file: {temp_filename}")
        
        # Encrypt the file
        print("Encrypting...")
        cryptFile("e", password, temp_filename, encrypted_filename)
        print(f"Encrypted file created: {encrypted_filename}")
        
        # Decrypt the file
        print("Decrypting...")
        cryptFile("d", password, encrypted_filename, decrypted_filename)
        print(f"Decrypted file created: {decrypted_filename}")
        
        # Verify the content
        with open(decrypted_filename, 'r') as f:
            decrypted_content = f.read()
        print(f"Decrypted content: {decrypted_content}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up temporary files
        for filename in [temp_filename, encrypted_filename, decrypted_filename]:
            if os.path.exists(filename):
                os.unlink(filename)
                print(f"Cleaned up: {filename}")


def example_2_error_handling():
    """Example 2: Demonstrating error handling"""
    print("\n=== Example 2: Error Handling ===")
    
    # Try to decrypt with wrong password
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write("Secret data")
        temp_filename = temp_file.name
    
    try:
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        encrypted_filename = temp_filename + ".aes"
        
        # Encrypt with correct password
        cryptFile("e", correct_password, temp_filename, encrypted_filename)
        print("File encrypted successfully")
        
        # Try to decrypt with wrong password
        try:
            cryptFile("d", wrong_password, encrypted_filename, temp_filename + ".failed")
            print("This shouldn't happen!")
        except ValueError as e:
            print(f"Expected error caught: {e}")
        
        # Try to encrypt non-existent file
        try:
            cryptFile("e", "password", "non_existent_file.txt", "output.aes")
            print("This shouldn't happen!")
        except FileNotFoundError as e:
            print(f"Expected error caught: {e}")
            
    finally:
        # Clean up
        for filename in [temp_filename, encrypted_filename]:
            if os.path.exists(filename):
                os.unlink(filename)


def example_3_batch_processing():
    """Example 3: Batch processing multiple files"""
    print("\n=== Example 3: Batch Processing ===")
    
    # Create multiple temporary files
    temp_files = []
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create test files
        for i in range(3):
            filename = os.path.join(temp_dir, f"test_file_{i}.txt")
            with open(filename, 'w') as f:
                f.write(f"This is test file number {i}")
            temp_files.append(filename)
        
        password = "batch_password"
        
        # Encrypt all files
        print("Encrypting files...")
        encrypted_files = []
        for filename in temp_files:
            encrypted_filename = filename + ".aes"
            try:
                cryptFile("e", password, filename, encrypted_filename)
                encrypted_files.append(encrypted_filename)
                print(f"  Encrypted: {os.path.basename(filename)}")
            except Exception as e:
                print(f"  Failed to encrypt {filename}: {e}")
        
        # Decrypt all files
        print("Decrypting files...")
        for encrypted_filename in encrypted_files:
            decrypted_filename = encrypted_filename.replace(".aes", ".decrypted")
            try:
                cryptFile("d", password, encrypted_filename, decrypted_filename)
                print(f"  Decrypted: {os.path.basename(encrypted_filename)}")
            except Exception as e:
                print(f"  Failed to decrypt {encrypted_filename}: {e}")
                
    finally:
        # Clean up temporary directory
        import shutil
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temporary directory: {temp_dir}")


def example_4_interactive_wrapper():
    """Example 4: Creating a custom interactive wrapper"""
    print("\n=== Example 4: Custom Interactive Wrapper ===")
    
    def custom_interactive_encrypt():
        """Custom function that adds extra features to the basic functionality"""
        print("Custom AesCrypt Wrapper")
        print("======================")
        
        # Get file path with validation
        while True:
            file_path = input("Enter file path to encrypt: ").strip()
            if os.path.exists(file_path):
                break
            print(f"File not found: {file_path}")
        
        # Get password with confirmation
        while True:
            password1 = input("Enter password: ")
            password2 = input("Confirm password: ")
            if password1 == password2:
                if len(password1) >= 8:
                    password = password1
                    break
                else:
                    print("Password must be at least 8 characters long")
            else:
                print("Passwords don't match")
        
        # Generate output filename
        output_path = file_path + ".aes"
        
        try:
            cryptFile("e", password, file_path, output_path)
            print(f"Successfully encrypted to: {output_path}")
            
            # Show file sizes
            original_size = os.path.getsize(file_path)
            encrypted_size = os.path.getsize(output_path)
            print(f"Original size: {original_size} bytes")
            print(f"Encrypted size: {encrypted_size} bytes")
            
        except Exception as e:
            print(f"Encryption failed: {e}")
    
    # For demonstration, we'll skip the actual interactive part
    # and just show the concept
    print("This would run a custom interactive encryption process")
    print("with password confirmation and file size reporting.")


def main_examples():
    """Run all examples"""
    print("AesCrypt Usage Examples")
    print("=======================")
    
    try:
        example_1_basic_encryption()
        example_2_error_handling()
        example_3_batch_processing()
        example_4_interactive_wrapper()
        
        print("\n=== All Examples Completed ===")
        print("You can also run the original interactive mode:")
        print("python ../AesCrypt.py")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main_examples()