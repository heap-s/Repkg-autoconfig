import os
import xml.etree.ElementTree as ET
from datetime import datetime
import glob

def validate_xml_structure(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        log_messages = []

        if root.tag != 'packages':
            log_messages.append(f"Error: Root element should be 'packages' in {file_path}")
        else:
            log_messages.append(f"Success: Root element is 'packages' in {file_path}")

        for package in root.findall('package'):
            required_elements = ['packageName', 'version', 'sha256', 'url']
            for element in required_elements:
                if package.find(element) is None:
                    log_messages.append(f"Error: Missing '{element}' in a package in {file_path}")
                else:
                    log_messages.append(f"Success: Found '{element}' in a package in {file_path}")

        return log_messages
    except ET.ParseError as e:
        return [f"Error: XML parsing error in {file_path}: {str(e)}"]

def validate_version_date(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    current_date = datetime.now().strftime("%Y%m%d")

    log_messages = []

    for package in root.findall('package'):
        package_name = package.find('packageName').text
        version = package.find('version').text
        if current_date not in version:
            log_messages.append(f"Error: Version does not contain current date for package '{package_name}' in {file_path}")
        else:
            log_messages.append(f"Success: Version contains current date for package '{package_name}' in {file_path}")

    return log_messages

def main():
    directories = ['examples', 'config']
    xml_files = []

    for directory in directories:
        xml_files.extend(glob.glob(f"{directory}/*.xml"))

    all_valid = True

    for file_path in xml_files:
        print(f"\nValidating {file_path}:")
        
        structure_messages = validate_xml_structure(file_path)
        for message in structure_messages:
            print(message)
            if message.startswith("Error"):
                all_valid = False

        date_messages = validate_version_date(file_path)
        for message in date_messages:
            print(message)
            if message.startswith("Error"):
                all_valid = False

    if not all_valid:
        print("\nValidation failed. Please fix the errors above.")
        exit(1)
    else:
        print("\nAll XML files passed validation.")

if __name__ == "__main__":
    main()