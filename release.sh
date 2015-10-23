#!/bin/sh

# Get PyPI repo name (optional)
if [ -n "$1" ]; then
  pypi_repo="$1"
  pypi_repo_str="-r $1"
else
  pypi_repo="pypi.python.org"
  pypi_repo_str=""
fi

# Define some colors for echos
RED='\033[38;5;160m'
GREEN='\033[38;5;2m'
YELLOW='\033[38;5;3m'
BLUE='\033[38;5;39m'
MAGENTA='\033[38;5;5m'
CYAN='\033[38;5;6m'
WHITE='\033[38;5;7m'
BLACK='\033[38;5;8m'
NOCOLOR='\033[m'

# Get name and path of this script
script_name="$(basename "$0")"
script_path="$(cd "$(dirname "$0")" && pwd)"

# Only run from within script directory
if [[ "$PWD" != "$script_path" ]]; then
  echo "Please execute $script_name from inside the directory it's contained in"
  exit 1
fi

# Only run if git reports nothing changed
if [[ -n "$(git status --porcelain)" ]] ; then
  echo "Git reports 1 or more files changed, please commit all changes before running this script"
  exit 1
fi

# Set the path/name of the VERSION file
version_file="$script_path/VERSION"

# Get the current version
current_version=$(cat $version_file)
echo "${BLUE}Current version:${NOCOLOR} $current_version"

# Prompt user for the new version
new_version=''
while [[ $new_version = '' ]] ; do
  printf "${BLUE}Enter the new version: ${NOCOLOR}"
  read new_version
done

echo "${YELLOW}This script will update the VERSION file, create a"
echo "new git commit and tag, and upload a new package to"
echo "the $pypi_repo repo. Do you confirm? (${GREEN}y${YELLOW}/[${RED}n${YELLOW}])${NOCOLOR}"
read confirm
if [[ "$confirm" =~ ^[Yy]$ ]] ; then
  break
else
  echo "${RED}Aborting release...${NOCOLOR}"
  exit 0
fi

echo "${GREEN}Updating package to version ${new_version}${NOCOLOR}"

# Update version in VERSION file
echo $new_version > $version_file

# Make a git commit with the updated VERSION file
git add $version_file
git commit -m "Update package version"

# Make a git tag for this version
git tag -a $new_version

# Upload to PyPI
python setup.py sdist upload $pypi_repo_str
