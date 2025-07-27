#!/usr/bin/env python3
"""
Advanced Usage Examples for AesCrypt

This file demonstrates advanced usage patterns including integration
with other systems, configuration management, and complex workflows.
"""

import os
import sys
import json
import argparse
import hashlib
import logging
from pathlib import Path

# Add the parent directory to the path so we can import AesCrypt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pyAesCrypt
    from AesCrypt import cryptFile
except ImportError as e:
    print(f"Error: {e}")
    print("Please install pyAesCrypt: pip install pyAesCrypt")
    sys.exit(1)


class AesCryptManager:
    """
    Advanced wrapper class for AesCrypt functionality.
    
    Provides additional features like logging, configuration management,
    batch operations, and integrity verification.
    """
    
    def __init__(self, config_file=None):
        """Initialize the AesCrypt Manager with optional configuration."""
        self.config = self._load_config(config_file)
        self._setup_logging()
        
    def _load_config(self, config_file):
        """Load configuration from file or use defaults."""
        default_config = {
            "default_extension": ".aes",
            "backup_originals": False,
            "verify_integrity": True,
            "log_level": "INFO",
            "max_file_size_mb": 100
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
        
        return default_config
    
    def _setup_logging(self):
        """Setup logging based on configuration."""
        log_level = getattr(logging, self.config["log_level"].upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def calculate_checksum(self, file_path):
        """Calculate SHA-256 checksum of a file."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return None
    
    def encrypt_with_verification(self, password, input_file, output_file=None):
        """
        Encrypt a file with integrity verification.
        
        Returns a dictionary with operation results and metadata.
        """
        if output_file is None:
            output_file = input_file + self.config["default_extension"]
        
        # Check file size
        file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
        if file_size_mb > self.config["max_file_size_mb"]:
            raise ValueError(f"File size ({file_size_mb:.2f}MB) exceeds limit ({self.config['max_file_size_mb']}MB)")
        
        # Calculate original checksum if verification is enabled
        original_checksum = None
        if self.config["verify_integrity"]:
            original_checksum = self.calculate_checksum(input_file)
            self.logger.info(f"Original file checksum: {original_checksum}")
        
        # Perform encryption
        self.logger.info(f"Encrypting {input_file} to {output_file}")
        try:
            cryptFile("e", password, input_file, output_file)
            self.logger.info("Encryption completed successfully")
            
            # Verify by decrypting to temporary file and checking checksum
            if self.config["verify_integrity"] and original_checksum:
                self.logger.info("Verifying encryption integrity...")
                temp_decrypt_file = output_file + ".verify_temp"
                try:
                    cryptFile("d", password, output_file, temp_decrypt_file)
                    decrypt_checksum = self.calculate_checksum(temp_decrypt_file)
                    
                    if decrypt_checksum == original_checksum:
                        self.logger.info("Integrity verification passed")
                        integrity_verified = True
                    else:
                        self.logger.error("Integrity verification failed!")
                        integrity_verified = False
                    
                    # Clean up temporary file
                    os.unlink(temp_decrypt_file)
                    
                except Exception as e:
                    self.logger.error(f"Integrity verification failed: {e}")
                    integrity_verified = False
            else:
                integrity_verified = None
            
            return {
                "success": True,
                "input_file": input_file,
                "output_file": output_file,
                "original_size": os.path.getsize(input_file),
                "encrypted_size": os.path.getsize(output_file),
                "original_checksum": original_checksum,
                "integrity_verified": integrity_verified
            }
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "input_file": input_file,
                "output_file": output_file
            }
    
    def batch_encrypt_directory(self, directory_path, password, pattern="*", recursive=False):
        """
        Encrypt all files in a directory matching a pattern.
        
        Returns a list of operation results.
        """
        self.logger.info(f"Starting batch encryption of {directory_path}")
        
        path_obj = Path(directory_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find files to encrypt
        if recursive:
            files_to_encrypt = list(path_obj.rglob(pattern))
        else:
            files_to_encrypt = list(path_obj.glob(pattern))
        
        # Filter out already encrypted files and directories
        files_to_encrypt = [
            f for f in files_to_encrypt 
            if f.is_file() and not str(f).endswith(self.config["default_extension"])
        ]
        
        self.logger.info(f"Found {len(files_to_encrypt)} files to encrypt")
        
        results = []
        for file_path in files_to_encrypt:
            try:
                result = self.encrypt_with_verification(password, str(file_path))
                results.append(result)
                
                if result["success"]:
                    self.logger.info(f"Successfully encrypted: {file_path.name}")
                else:
                    self.logger.error(f"Failed to encrypt: {file_path.name}")
                    
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "input_file": str(file_path)
                })
        
        return results
    
    def generate_report(self, results, output_file="encryption_report.json"):
        """Generate a detailed report of batch operations."""
        report = {
            "timestamp": str(Path().cwd()),
            "total_files": len(results),
            "successful": len([r for r in results if r.get("success", False)]),
            "failed": len([r for r in results if not r.get("success", False)]),
            "total_original_size": sum(r.get("original_size", 0) for r in results if r.get("success", False)),
            "total_encrypted_size": sum(r.get("encrypted_size", 0) for r in results if r.get("success", False)),
            "operations": results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Report generated: {output_file}")
        return report


def example_1_advanced_encryption():
    """Example 1: Advanced encryption with verification and logging"""
    print("=== Advanced Encryption with Verification ===")
    
    # Create a manager instance
    manager = AesCryptManager()
    
    # Create a test file
    test_file = "test_advanced.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test file for advanced encryption.\n" * 100)
    
    try:
        # Encrypt with verification
        result = manager.encrypt_with_verification(
            password="advanced_password_123",
            input_file=test_file
        )
        
        print(f"Encryption result: {result}")
        
        if result["success"]:
            print(f"Original size: {result['original_size']} bytes")
            print(f"Encrypted size: {result['encrypted_size']} bytes")
            print(f"Compression ratio: {result['encrypted_size']/result['original_size']:.2f}")
            print(f"Integrity verified: {result['integrity_verified']}")
        
    finally:
        # Clean up
        for file in [test_file, test_file + ".aes"]:
            if os.path.exists(file):
                os.unlink(file)


def example_2_batch_with_config():
    """Example 2: Batch processing with custom configuration"""
    print("\n=== Batch Processing with Configuration ===")
    
    # Create a configuration file
    config = {
        "default_extension": ".encrypted",
        "verify_integrity": True,
        "log_level": "DEBUG",
        "max_file_size_mb": 50
    }
    
    config_file = "aescrypt_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    try:
        # Create test directory structure
        test_dir = "test_batch_dir"
        os.makedirs(test_dir, exist_ok=True)
        
        # Create test files
        for i in range(3):
            with open(f"{test_dir}/file_{i}.txt", 'w') as f:
                f.write(f"Content of file {i}\n" * 50)
        
        # Initialize manager with config
        manager = AesCryptManager(config_file)
        
        # Perform batch encryption
        results = manager.batch_encrypt_directory(
            directory_path=test_dir,
            password="batch_password_456",
            pattern="*.txt"
        )
        
        # Generate report
        report = manager.generate_report(results)
        
        print(f"Batch encryption completed:")
        print(f"  Total files: {report['total_files']}")
        print(f"  Successful: {report['successful']}")
        print(f"  Failed: {report['failed']}")
        
    finally:
        # Clean up
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        for file in [config_file, "encryption_report.json"]:
            if os.path.exists(file):
                os.unlink(file)


def example_3_command_line_interface():
    """Example 3: Command-line interface for advanced operations"""
    print("\n=== Command-line Interface Example ===")
    
    def create_cli_parser():
        """Create argument parser for command-line usage"""
        parser = argparse.ArgumentParser(
            description="Advanced AesCrypt Command-line Interface",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s encrypt -f document.pdf -p mypassword
  %(prog)s batch -d /path/to/files -p password --pattern "*.txt"
  %(prog)s decrypt -f document.pdf.aes -p mypassword
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Encrypt command
        encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a single file')
        encrypt_parser.add_argument('-f', '--file', required=True, help='Input file path')
        encrypt_parser.add_argument('-p', '--password', required=True, help='Encryption password')
        encrypt_parser.add_argument('-o', '--output', help='Output file path (optional)')
        encrypt_parser.add_argument('--verify', action='store_true', help='Verify encryption integrity')
        
        # Batch command
        batch_parser = subparsers.add_parser('batch', help='Batch encrypt directory')
        batch_parser.add_argument('-d', '--directory', required=True, help='Directory to encrypt')
        batch_parser.add_argument('-p', '--password', required=True, help='Encryption password')
        batch_parser.add_argument('--pattern', default='*', help='File pattern to match')
        batch_parser.add_argument('--recursive', action='store_true', help='Process subdirectories')
        batch_parser.add_argument('--report', help='Output report file path')
        
        # Decrypt command
        decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt a file')
        decrypt_parser.add_argument('-f', '--file', required=True, help='Encrypted file path')
        decrypt_parser.add_argument('-p', '--password', required=True, help='Decryption password')
        decrypt_parser.add_argument('-o', '--output', help='Output file path (optional)')
        
        return parser
    
    # Simulate command-line usage
    parser = create_cli_parser()
    
    print("CLI Parser created successfully!")
    print("This would handle commands like:")
    print("  python advanced_usage.py encrypt -f document.txt -p password123")
    print("  python advanced_usage.py batch -d /home/user/documents -p password123")
    
    # Show help
    print("\nHelp output:")
    parser.print_help()


def example_4_integration_patterns():
    """Example 4: Integration with other systems"""
    print("\n=== Integration Patterns ===")
    
    class BackupSystem:
        """Example backup system integration"""
        
        def __init__(self, backup_dir="backups"):
            self.backup_dir = backup_dir
            os.makedirs(backup_dir, exist_ok=True)
            self.crypto_manager = AesCryptManager()
        
        def secure_backup(self, file_path, password):
            """Create an encrypted backup of a file"""
            import shutil
            from datetime import datetime
            
            # Generate timestamped backup name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.basename(file_path)}_{timestamp}.backup"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Copy file to backup location
            shutil.copy2(file_path, backup_path)
            
            # Encrypt the backup
            encrypted_backup = backup_path + ".aes"
            result = self.crypto_manager.encrypt_with_verification(
                password, backup_path, encrypted_backup
            )
            
            # Remove unencrypted backup
            if result["success"]:
                os.unlink(backup_path)
                return encrypted_backup
            else:
                raise Exception(f"Backup encryption failed: {result.get('error')}")
    
    # Demonstrate backup system
    print("Creating secure backup system...")
    
    # Create test file
    test_file = "important_document.txt"
    with open(test_file, 'w') as f:
        f.write("This is an important document that needs secure backup.")
    
    try:
        backup_system = BackupSystem()
        encrypted_backup = backup_system.secure_backup(test_file, "backup_password_789")
        print(f"Secure backup created: {encrypted_backup}")
        
    finally:
        # Clean up
        import shutil
        if os.path.exists("backups"):
            shutil.rmtree("backups")
        if os.path.exists(test_file):
            os.unlink(test_file)


def main():
    """Run all advanced examples"""
    print("AesCrypt Advanced Usage Examples")
    print("================================")
    
    try:
        example_1_advanced_encryption()
        example_2_batch_with_config()
        example_3_command_line_interface()
        example_4_integration_patterns()
        
        print("\n=== All Advanced Examples Completed ===")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()