import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import glob
import subprocess

def get_last_modified_date(file_path):
    try:
        result = subprocess.run(['git', 'log', '-1', '--format=%cd', '--date=format:%Y%m%d', file_path], 
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # If the file is not in git, use the file system's last modified date
        return datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y%m%d')

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
    last_modified_date = get_last_modified_date(file_path)

    log_messages = []

    for package in root.findall('package'):
        package_name = package.find('packageName').text
        version = package.find('version').text
        version_date = version.split('-')[-1]

        if version_date != last_modified_date:
            log_messages.append(f"Error: Version date {version_date} does not match last modified date {last_modified_date} for package '{package_name}' in {file_path}")
        else:
            log_messages.append(f"Success: Version date matches last modified date for package '{package_name}' in {file_path}")

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