#!/usr/bin/env python3
"""
Test Suite for AesCrypt Components

This file demonstrates how to create comprehensive tests for the AesCrypt
utility, including unit tests, integration tests, and performance tests.
"""

import os
import sys
import unittest
import tempfile
import shutil
import time
from unittest.mock import patch, Mock

# Add the parent directory to the path so we can import AesCrypt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pyAesCrypt
    from AesCrypt import cryptFile, get_data_from_user, main
except ImportError as e:
    print(f"Error: {e}")
    print("Please install pyAesCrypt: pip install pyAesCrypt")
    sys.exit(1)


class TestAesCryptBasic(unittest.TestCase):
    """Basic unit tests for AesCrypt functions"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        self.test_content = "This is test content for encryption testing."
        
        # Create test file
        with open(self.test_file, 'w') as f:
            f.write(self.test_content)
    
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.test_dir)
    
    def test_encrypt_decrypt_cycle(self):
        """Test that encryption followed by decryption preserves content"""
        password = "test_password_123"
        encrypted_file = self.test_file + ".aes"
        decrypted_file = self.test_file + ".decrypted"
        
        # Encrypt
        cryptFile("e", password, self.test_file, encrypted_file)
        self.assertTrue(os.path.exists(encrypted_file))
        
        # Decrypt
        cryptFile("d", password, encrypted_file, decrypted_file)
        self.assertTrue(os.path.exists(decrypted_file))
        
        # Verify content
        with open(decrypted_file, 'r') as f:
            decrypted_content = f.read()
        
        self.assertEqual(self.test_content, decrypted_content)
    
    def test_wrong_password_raises_error(self):
        """Test that wrong password raises ValueError during decryption"""
        password = "correct_password"
        wrong_password = "wrong_password"
        encrypted_file = self.test_file + ".aes"
        decrypted_file = self.test_file + ".decrypted"
        
        # Encrypt with correct password
        cryptFile("e", password, self.test_file, encrypted_file)
        
        # Try to decrypt with wrong password
        with self.assertRaises(ValueError):
            cryptFile("d", wrong_password, encrypted_file, decrypted_file)
    
    def test_nonexistent_file_raises_error(self):
        """Test that encrypting non-existent file raises FileNotFoundError"""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")
        output_file = nonexistent_file + ".aes"
        
        with self.assertRaises(FileNotFoundError):
            cryptFile("e", "password", nonexistent_file, output_file)
    
    def test_empty_file_encryption(self):
        """Test encryption and decryption of empty files"""
        empty_file = os.path.join(self.test_dir, "empty.txt")
        open(empty_file, 'w').close()  # Create empty file
        
        password = "empty_test_password"
        encrypted_file = empty_file + ".aes"
        decrypted_file = empty_file + ".decrypted"
        
        # Encrypt empty file
        cryptFile("e", password, empty_file, encrypted_file)
        self.assertTrue(os.path.exists(encrypted_file))
        
        # Decrypt empty file
        cryptFile("d", password, encrypted_file, decrypted_file)
        self.assertTrue(os.path.exists(decrypted_file))
        
        # Verify file is still empty
        self.assertEqual(os.path.getsize(decrypted_file), 0)


class TestAesCryptInteractive(unittest.TestCase):
    """Tests for interactive functionality"""
    
    @patch('builtins.input')
    def test_get_data_from_user_encrypt(self, mock_input):
        """Test get_data_from_user function for encryption"""
        # Mock user inputs
        mock_input.side_effect = ['e', 'test.txt', 'password123', 'test.txt.aes']
        
        result = get_data_from_user()
        
        expected = {
            'action': 'e',
            'pass': 'password123',
            'path': 'test.txt',
            'output': 'test.txt.aes'
        }
        
        self.assertEqual(result, expected)
    
    @patch('builtins.input')
    def test_get_data_from_user_decrypt(self, mock_input):
        """Test get_data_from_user function for decryption"""
        # Mock user inputs
        mock_input.side_effect = ['d', 'test.txt.aes', 'password123', 'test.txt']
        
        result = get_data_from_user()
        
        expected = {
            'action': 'd',
            'pass': 'password123',
            'path': 'test.txt.aes',
            'output': 'test.txt'
        }
        
        self.assertEqual(result, expected)
    
    @patch('builtins.input')
    def test_get_data_from_user_invalid_then_valid(self, mock_input):
        """Test get_data_from_user with invalid input followed by valid input"""
        # Mock user inputs: invalid, then valid
        mock_input.side_effect = ['x', 'invalid', 'encrypt', 'test.txt', 'pass', 'out.aes']
        
        result = get_data_from_user()
        
        self.assertEqual(result['action'], 'e')
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_successful_encryption(self, mock_print, mock_input):
        """Test main function with successful encryption"""
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("Test content")
            temp_filename = temp_file.name
        
        try:
            # Mock user inputs
            mock_input.side_effect = [
                'e',  # encrypt
                temp_filename,  # input file
                'test_password',  # password
                temp_filename + '.aes'  # output file
            ]
            
            # Run main function
            main()
            
            # Check that success message was printed
            mock_print.assert_any_call("Finish!")
            
            # Check that encrypted file was created
            self.assertTrue(os.path.exists(temp_filename + '.aes'))
            
        finally:
            # Clean up
            for file in [temp_filename, temp_filename + '.aes']:
                if os.path.exists(file):
                    os.unlink(file)


class TestAesCryptPerformance(unittest.TestCase):
    """Performance tests for AesCrypt operations"""
    
    def setUp(self):
        """Set up performance test fixtures"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after performance tests"""
        shutil.rmtree(self.test_dir)
    
    def test_large_file_performance(self):
        """Test encryption/decryption performance with larger files"""
        # Create a 1MB test file
        large_file = os.path.join(self.test_dir, "large_test.txt")
        content = "A" * 1024  # 1KB string
        
        with open(large_file, 'w') as f:
            for _ in range(1024):  # Write 1MB
                f.write(content)
        
        password = "performance_test_password"
        encrypted_file = large_file + ".aes"
        decrypted_file = large_file + ".decrypted"
        
        # Measure encryption time
        start_time = time.time()
        cryptFile("e", password, large_file, encrypted_file)
        encryption_time = time.time() - start_time
        
        # Measure decryption time
        start_time = time.time()
        cryptFile("d", password, encrypted_file, decrypted_file)
        decryption_time = time.time() - start_time
        
        # Performance assertions (these may need adjustment based on system)
        self.assertLess(encryption_time, 10.0, "Encryption took too long")
        self.assertLess(decryption_time, 10.0, "Decryption took too long")
        
        # Verify file integrity
        self.assertEqual(
            os.path.getsize(large_file),
            os.path.getsize(decrypted_file)
        )
        
        print(f"Performance: Encryption={encryption_time:.2f}s, Decryption={decryption_time:.2f}s")
    
    def test_multiple_files_batch_performance(self):
        """Test performance with multiple small files"""
        num_files = 100
        files_created = []
        
        # Create multiple small files
        for i in range(num_files):
            file_path = os.path.join(self.test_dir, f"batch_test_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Content of file {i}\n" * 10)
            files_created.append(file_path)
        
        password = "batch_performance_test"
        
        # Measure batch encryption time
        start_time = time.time()
        for file_path in files_created:
            encrypted_file = file_path + ".aes"
            cryptFile("e", password, file_path, encrypted_file)
        batch_encryption_time = time.time() - start_time
        
        # Performance assertion
        avg_time_per_file = batch_encryption_time / num_files
        self.assertLess(avg_time_per_file, 0.1, "Average encryption time per file too high")
        
        print(f"Batch Performance: {num_files} files in {batch_encryption_time:.2f}s "
              f"({avg_time_per_file:.3f}s per file)")


class TestAesCryptEdgeCases(unittest.TestCase):
    """Tests for edge cases and error conditions"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_unicode_content(self):
        """Test encryption of files with unicode content"""
        unicode_file = os.path.join(self.test_dir, "unicode_test.txt")
        unicode_content = "Test with unicode: áéíóú 中文 🎉 🔐"
        
        with open(unicode_file, 'w', encoding='utf-8') as f:
            f.write(unicode_content)
        
        password = "unicode_password"
        encrypted_file = unicode_file + ".aes"
        decrypted_file = unicode_file + ".decrypted"
        
        # Encrypt and decrypt
        cryptFile("e", password, unicode_file, encrypted_file)
        cryptFile("d", password, encrypted_file, decrypted_file)
        
        # Verify unicode content preserved
        with open(decrypted_file, 'r', encoding='utf-8') as f:
            decrypted_content = f.read()
        
        self.assertEqual(unicode_content, decrypted_content)
    
    def test_special_characters_in_password(self):
        """Test encryption with special characters in password"""
        test_file = os.path.join(self.test_dir, "special_pass_test.txt")
        with open(test_file, 'w') as f:
            f.write("Testing special characters in password")
        
        # Password with various special characters
        special_password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:,.<>?"
        encrypted_file = test_file + ".aes"
        decrypted_file = test_file + ".decrypted"
        
        # Should work without issues
        cryptFile("e", special_password, test_file, encrypted_file)
        cryptFile("d", special_password, encrypted_file, decrypted_file)
        
        # Verify files exist
        self.assertTrue(os.path.exists(decrypted_file))
    
    def test_very_long_password(self):
        """Test encryption with very long password"""
        test_file = os.path.join(self.test_dir, "long_pass_test.txt")
        with open(test_file, 'w') as f:
            f.write("Testing very long password")
        
        # Create a very long password (1000 characters)
        long_password = "a" * 1000
        encrypted_file = test_file + ".aes"
        decrypted_file = test_file + ".decrypted"
        
        # Should work without issues
        cryptFile("e", long_password, test_file, encrypted_file)
        cryptFile("d", long_password, encrypted_file, decrypted_file)
        
        self.assertTrue(os.path.exists(decrypted_file))


def run_test_suite():
    """Run the complete test suite with reporting"""
    print("AesCrypt Test Suite")
    print("==================")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAesCryptBasic))
    suite.addTests(loader.loadTestsFromTestCase(TestAesCryptInteractive))
    suite.addTests(loader.loadTestsFromTestCase(TestAesCryptPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestAesCryptEdgeCases))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)