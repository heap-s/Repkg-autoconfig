import xml.etree.ElementTree as ET
import hashlib
import requests
import sys
import os
from lxml import etree

def download_file(url, filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def calculate_sha256(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_package(package):
    package_name = package.find('packageName').text
    url = package.find('url').text
    expected_sha256 = package.find('sha256').text

    print(f"\nVerifying package: {package_name}")
    
    # Download the installer
    installer_filename = f"{package_name}_installer.exe"
    print(f"Downloading installer from {url}")
    download_file(url, installer_filename)

    # Calculate the SHA256 of the downloaded file
    print("Calculating SHA256 of the downloaded installer")
    actual_sha256 = calculate_sha256(installer_filename)

    # Compare the SHA256 hashes
    print(f"Expected SHA256: {expected_sha256}")
    print(f"Actual SHA256:   {actual_sha256}")

    if actual_sha256.lower() == expected_sha256.lower():
        print("SHA256 verification successful!")
        return True
    else:
        print("Error: SHA256 verification failed!")
        return False

def main():
    file_path = 'tests/test-autoconfig.xml'
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    # Check file size
    if os.path.getsize(file_path) == 0:
        print(f"Error: File '{file_path}' is empty.")
        return

    # Try to read file contents
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"File contents:\n{content}")
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # If all checks pass, try to parse the XML
    parser = etree.XMLParser(remove_blank_text=True)
    try:
        tree = etree.parse(file_path, parser)
        # Rest of your code...
    except etree.XMLSyntaxError as e:
        print(f"XML parsing error: {e}")

    # Parse the XML file
    root = tree.getroot()

    # Find all packages
    packages = root.findall(".//package")
    if not packages:
        print("Error: No packages found in XML")
        sys.exit(1)

    all_verified = True

    for package in packages:
        if not verify_package(package):
            all_verified = False

    if not all_verified:
        print("\nError: One or more package verifications failed!")
        sys.exit(1)
    else:
        print("\nAll packages verified successfully!")

if __name__ == "__main__":
    main()
