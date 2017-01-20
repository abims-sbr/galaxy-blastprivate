
ABIMS - ROSCOFF - 01/08/14 - E. Prudent

--------------------------------
Privatize BLAST tools on Galaxy
--------------------------------

I. File list
------------

MakeToolsBlast.py		Module to automate the creation of privatized BLAST tools
blast_filter.py			File to restricit access to BLAST tools 
blast_rules.py			File to restricit execution to BLAST tools 
VisuBlast.xml			Wrapper xml to Visualize BLAST Tools
VisuBlast.py			Wrapper python to Visualize BLAST Tools
XmlCreate.py			Template XML to create BLAST tools
Pictures/				Directory of pictures for VisuBlast

II. To do
---------

Place the FOLDER containing all this file in galaxy-dist.
Execute install.sh
>> ./install.sh 

III. Install overview
---------------------
```
|-----------------|
|   galaxy-dist   |--------> MakeToolsBlast.py
|-----------------|--------> XmlCreate.py	
	|
	|-----------|
	|   tools   |
	|-----------|
	|	|		
	|	|-----------|
	|	|   blast   |--------> VisuBlast.xml
	|	|-----------|--------> VisuBlast.py
	|		
	|---------------|
	|   tool-data   |
	|---------------|
	|	|		
	|	|----------------|
	|	|   BlastAbims   |--------> Pictures/
	|	|----------------|		
	|
	|---------|
	|   lib   |
	|---------|
		|		
		|------------|
		|   galaxy   |
		|------------|
			|		
			|----------|
			|   jobs   |
			|----------|
			|	|		
			|	|-----------|
			|	|   rules   |--------> blast_rules.py
			|	|-----------|
			|
			|-----------|
			|   tools   |
			|-----------|
				|		
				|-------------|
				|   filters   |--------> blast_filters.py
				|-------------|
```


Historic contributors
---------------------

 - Emma Prudent - [ABiMS](http://abims.sb-roscoff.fr/) / [IFB](http://www.france-bioinformatique.fr/) - [UPMC](www.upmc.fr)/[CNRS](www.cnrs.fr) - [Station Biologique de Roscoff](http://www.sb-roscoff.fr/) - France
 - Erwan Corre  - [ABiMS](http://abims.sb-roscoff.fr/) / [IFB](http://www.france-bioinformatique.fr/) - [UPMC](www.upmc.fr)/[CNRS](www.cnrs.fr) - [Station Biologique de Roscoff](http://www.sb-roscoff.fr/) - France
 - Christophe Caron  - [ABiMS](http://abims.sb-roscoff.fr/) / [IFB](http://www.france-bioinformatique.fr/) - [UPMC](www.upmc.fr)/[CNRS](www.cnrs.fr) - [Station Biologique de Roscoff](http://www.sb-roscoff.fr/) - France
