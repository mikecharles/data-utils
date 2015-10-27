#!/bin/sh

# Usage
usage() {
  printf "$(basename "$0") [-h] [PYPIREPO]\n"
  printf "  where:\n"
  printf "    -h        show this help text:\n"
  printf "    PYPIREPO  optional PyPI repo (defaults to pypi.org)\n"
}

# Check command-line args
while getopts ':h' option; do
  case "$option" in
    h)
      usage
      exit
      ;;
   \?) printf "Invalid option: -%s\n" "$OPTARG" >&2
       usage >&2
       exit 1
       ;;
  esac
done
shift $((OPTIND - 1))

# Get PyPI repo name (optional)
if [ -n "$1" ]; then
  pypi_repo="$1"
  pypi_repo_str="-r $1"
else
  pypi_repo="pypi.python.org"
  pypi_repo_str=""
fi

# Define some colors for printfs
RED='\e[0;31m'
GREEN='\e[0;32m'
YELLOW='\e[0;33m'
BLUE='\e[0;34m'
MAGENTA='\e[0;35m'
CYAN='\e[0;36m'
WHITE='\e[0;37m'
BLACK='\e[0;38m'
BOLDYELLOW='\e[1;33m'
NOCOLOR='\e[m'

# Get name and path of this script
script_name="$(basename "$0")"
script_path="$(cd "$(dirname "$0")" && pwd)"

# Only run from within script directory
if [[ "$PWD" != "$script_path" ]]; then
  printf "Please execute $script_name from inside the directory it's contained in\n"
  exit 1
fi

# Only run if git reports nothing changed
if [[ -n "$(git status --porcelain)" ]] ; then
  printf "${RED}Git reports 1 or more files changed, please commit all changes before running this script${NOCOLOR}\n"
  exit 1
fi

# Set the path/name of the VERSION file
version_file="$script_path/VERSION"

# Get the current version
current_version=$(cat $version_file)
printf "${BLUE}Current version:${NOCOLOR} $current_version\n"

# Prompt user for the new version
new_version=''
while [[ $new_version = '' ]] ; do
  printf "${BLUE}Enter the new version: ${NOCOLOR}"
  read new_version
done

# Print confirmation text
printf "${YELLOW}This script will update the VERSION file, create a\n"
printf "new git commit and tag, and upload an updated package\n"
printf "to the ${BOLDYELLOW}$pypi_repo${YELLOW} repo. Do you confirm? (${GREEN}y${YELLOW}/[${RED}n${YELLOW}])${NOCOLOR}\n"
read confirm

# Get confirmation to proceed or not
if [[ "$confirm" =~ ^[Yy]$ ]] ; then
  break
else
  printf "${RED}Aborting release...${NOCOLOR}\n"
  exit 0
fi
printf "${GREEN}Updating package to version ${new_version}${NOCOLOR}\n"

# Update version in VERSION file
printf $new_version > $version_file

# Make a git commit with the updated VERSION file
git add $version_file
git commit -m "Update package version"

# Make a git tag for this version
git tag -a $new_version

# Upload to PyPI
python setup.py sdist upload $pypi_repo_str
