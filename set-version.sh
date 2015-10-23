#!/bin/sh

# Get name and path of this script
script_name="$(basename "$0")"
script_path="$(cd "$(dirname "$0")" && pwd)"

# Only run from within script directory
if [[ "$PWD" != "$script_path" ]]; then
  echo "Please execute $script_name from inside the directory it's contained in"
  exit 1
fi

# Set the path/name of the VERSION file
version_file="$script_path/VERSION"

# Get the current version
current_version=$(cat $version_file)
echo "Current version: $current_version\n"

# Prompt user for the new version
new_version=''
while [[ $new_version = '' ]] ; do
  echo "Enter the new version:"
  read new_version
done

echo "Updating package to version $new_version"

# Update version in VERSION file
echo $new_version > $version_file

# Make a git commit with the updated VERSION file
