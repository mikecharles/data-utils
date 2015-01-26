#------------------------------------------------------------------------------
# Variables
#
TEMPDIRS   = logs work output

#------------------------------------------------------------------------------
# Rules
#
# Make required directories
mkdirs :
		mkdir -p $(TEMPDIRS)

# Clean (will delete directories created by mkdirs rule!)
clean :
		rm -rf $(TEMPDIRS)

# Copy the example config file to a live config file
copy_config_file :
		if [ ! -f library/config.yml ] ; then \
				cp library/config.yml.example library/config.yml ; \
		else \
				echo "library/config.yml already exists..." ; \
		fi;

# All
all : mkdirs copy_config_file
