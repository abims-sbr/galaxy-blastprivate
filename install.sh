#!/bin/bash

### INSTALL MAKETOOLSBLAST ###

GAL_FILTER="../lib/galaxy/tools/filters"
GAL_RULES="../lib/galaxy/jobs/rules"
GAL_TOOLS="../tools"
GAL_TOOL_DATA="../tool-data"

#---------Check File in directory for install
Complete=true

if [ ! -e blast_filter.py ]; then echo "/!\ Need blast_filter.py"; Complete=false; fi
if [ ! -e blast_rules.py ]; then echo "/!\ Need blast_rules.py"; Complete=false; fi
if [ ! -e VisuBlast.xml ]; then echo "/!\ Need VisuBlast.xml"; Complete=false; fi
if [ ! -e VisuBlast.py ]; then echo "/!\ Need VisuBlast.py"; Complete=false; fi
if [ ! -e XmlCreate.py ]; then echo "/!\ Need XmlCreate.py"; Complete=false; fi
if [ ! -d Pictures ]; then echo "/!\ Need Pictures directory"; Complete=false; fi

if [ $Complete==true ]; then

	#---------Move Blast Filter File 
	if [ -d "$GAL_FILTER" ]; then
	  cp blast_filter.py $GAL_FILTER
	else echo "/!\ Can't find $GAL_FILTER"
	fi

	#---------Move Blast Rules File 
	if [ -d "$GAL_RULES" ]; then
	  cp blast_rules.py $GAL_RULES
	else echo "/!\ Can't find $GAL_RULES"
	fi

	#---------Create Blast Directory in Tools with VisuBlast tools
	if [ -d "$GAL_TOOLS" ]; then
		if [ ! -d "$GAL_TOOLS"/blast ]; then
	  		mkdir "$GAL_TOOLS"/blast
		fi
		cp VisuBlast* "$GAL_TOOLS"/blast
	else echo "/!\ Can't find $GAL_TOOLS"
	fi

	#---------Create BlastAbims Directory in Tool_data with Pictures
	if [ -d "$GAL_TOOL_DATA" ]; then
		if [ ! -d "$GAL_TOOL_DATA"/BlastAbims ]; then
	  		mkdir "$GAL_TOOL_DATA"/BlastAbims
		fi
		cp -R Pictures "$GAL_TOOL_DATA"/BlastAbims
	else echo "/!\ Can't find $GAL_TOOL_DATA"
	fi

	#---------Check universe_wsgi.ini
	if [ -e ../universe_wsgi.ini ]; then 
		REQ=$(grep -R "tool_filters = blast_filter:generique_restrict_blast" ../universe_wsgi.ini)
		echo $REQ
		if [ -z "$REQ" ]; then
			cp ../universe_wsgi.ini ../universe_wsgi.ini.tmp
			sed '/Application and filtering/a tool_filters = blast_filter:generique_restrict_blast' ../universe_wsgi.ini.tmp > ../universe_wsgi.ini
		fi
	else cp universe_wsgi.ini ../
	fi

fi

