#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bioblend.galaxy import GalaxyInstance, GalaxyClient
from bioblend.galaxy.client import Client
from bioblend.galaxy.groups import GroupsClient

from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parse

import sys, subprocess, os, codecs, argparse, re, time, requests, json

#-----------BEFORE RUNNING-----------------------#
#
# 1\ Put .loc file for protein and nucleotide bases in ./tool-data/ (blastdb_projName.loc and blastdb_p_projName.loc)
# 2\ Check filter file blast_filter.py in ./lib/galaxy/tools/filters/
# 3\ Check rules file blast_rules.py in ./lib/galaxy/jobs/rules/
# 4\ Check tool filter declaration in univers_wsgi.ini : tool_filters = blast_filter:generique_restrict_blast
#
#------------------------------------------------#

APIKEY = "7fd3ba90d3a031f8b2a1de815e16dd4b"
URL = "galaxy4emma.sb-roscoff.fr:8080"
DIR = "/w/galaxy/galaxy4emma/galaxy-dist"

TEMPLATE_XML = "XmlCreate.py"

class ProjectBlast():
	
	def __init__(self, ProjectName, UsersList, url=URL, apiKey=APIKEY,verbose=False) :
	
		global DIR

		self.ApiKey = apiKey
		self.Url = url
		self.P = ProjectName.capitalize() 
		self.UsersList = UsersList 
		
		self.dir = DIR

		self.v = verbose
		self.bases = ["prot","nuc"]
		self.lbases = []
 
		self.check_files()
		if self.v : print "Check File : Done."
		self.i = GalaxyInstance(self.Url,self.ApiKey)
		self.run()

#----------------------------------------------------------------------------------------#	
	def check_files(self) :

		"""
		Check that all configs files are in palce
		"""

		if not os.path.exists("%s/tool-data/blastdb_%s.loc" % (self.dir,self.P.lower())) :
			self.bases.remove("nuc")
		if not os.path.exists("%s/tool-data/blastdb_p_%s.loc" % (self.dir,self.P.lower())) :
			self.bases.remove("prot")

		if self.bases == [] :
			raise SystemExit ('/!\ No database file blastdb_{0}.loc/blastdb_p_{0}.loc'.format(self.P.lower()))
		if not os.path.exists("%s/lib/galaxy/tools/filters/blast_filter.py" % self.dir) : 
			raise SystemExit ("/!\ lib/galaxy/tools/filters/blast_filter.py is missing")
		if not os.path.exists("%s/lib/galaxy/jobs/rules/blast_rules.py" % self.dir) :
			raise SystemExit ("/!\ lib/galaxy/jobs/rules/blast_rules.py is missing")
		if not os.popen('grep -R "tool_filters = blast_filter:generique_restrict_blast" %s/universe_wsgi.ini' % self.dir).read() : 
			raise SystemExit ("/!\ Tool filter declaration is missing in universe_wsgi.ini")


#----------------------------------------------------------------------------------------#	
	def run(self) :

		"""
		Control the sequence of steps
		"""

		#-----Save config file--------------------------------------------------------------#
		if not os.path.exists("/tmp/SaveConfGalaxy"): os.makedirs("/tmp/SaveConfGalaxy")
		os.system("cp tool_conf.xml /tmp/SaveConfGalaxy/tool_conf_%s" % time.strftime('%d%m%y_%Hh%M',time.localtime()))
		os.system("cp job_conf.xml /tmp/SaveConfGalaxy/job_conf_%s" % time.strftime('%d%m%y_%Hh%M',time.localtime()))
		#-----------------------------------------------------------------------------------#

		self.add_group()
		self.add_tools()
		self.update_tool_conf()
		self.update_job_conf()
		#os.system("sh ~/run.sh restart") # Restart Galaxy

#----------------------------------------------------------------------------------------#	
	def add_tools(self) :
		
		"""
		Creating xml files for the tool through a generator
		"""

		if not os.path.exists("%s/tools/blast" % self.dir): os.makedirs("%s/tools/blast" % self.dir)
		if os.path.exists("%s/tools/blast/%s" % (self.dir,self.P.lower())) : raise SystemExit ("Xml files for tools already exist")

		os.system("mkdir %s/tools/blast/%s" % (self.dir,self.P.lower()))

		if "nuc" in self.bases :
			self.lbases.extend(["tblastn","tblastx","blastn"])
			os.system("python {3} {0} 'blastn' > {2}/tools/blast/{0}/Blastn_{1}.xml".format(self.P.lower(),self.P,self.dir,TEMPLATE_XML))
			os.system("python {3} {0} 'blastx' > {2}/tools/blast/{0}/Tblastn_{1}.xml".format(self.P.lower(),self.P,self.dir,TEMPLATE_XML))
			os.system("python {3} {0} 'tblastx'> {2}/tools/blast/{0}/Tblastx_{1}.xml".format(self.P.lower(),self.P,self.dir,TEMPLATE_XML))

		if "prot" in self.bases : 
			self.lbases.extend(["blastp","blastx"])
			os.system("python {3} {0} 'blastp' > {2}/tools/blast/{0}/Blastp_{1}.xml".format(self.P.lower(),self.P,self.dir,TEMPLATE_XML))
			os.system("python {3} {0} 'tblastn'> {2}/tools/blast/{0}/Blastx_{1}.xml".format(self.P.lower(),self.P,self.dir,TEMPLATE_XML))

		if self.v : print "Add Tools : Done."

#----------------------------------------------------------------------------------------#	
	def update_tool_conf(self) :

		"""
		Update tool_conf.xml file by integrating the Blast tools
		"""

		filename = "%s/tool_conf.xml" % self.dir
		tool_conf = parse(filename)
		
		#-----UML balise creation----------------------------------------------------------------#
		sections = tool_conf.getElementsByTagName("section")
		for sec in sections :
			if sec.getAttribute('id') == "blast" :
				section = sec
				break

		for name in self.lbases :
			locals()["tool_%s" % name] = tool_conf.createElement("tool")
			locals()["tool_%s" % name].setAttribute("file","blast/%s/%s_%s.xml" % (self.P.lower(),name.capitalize(),self.P))
			section.appendChild(locals()["tool_%s" % name])
		#----------------------------------------------------------------------------------------#

		outfd=codecs.open(filename,"w","utf-8")
		tool_conf.writexml(outfd,addindent="\t",newl="\n")
		outfd.close()
		rmblank(filename)

		if self.v : print "Update tool_conf : Done."

#----------------------------------------------------------------------------------------#	
	def add_group(self) :
		
		"""
		Group's creation on Galaxy
		"""

		self.i.groups.create_group("G_%s" % self.P.capitalize(), self.UsersList, [])
		if self.v : print "Add Group : Done."

#----------------------------------------------------------------------------------------#	
	def update_job_conf(self) :

		"""
		Update job_conf.xml file by connecting tool to a Blast rules destination
		"""		
		
		filename = "%s/job_conf.xml" % self.dir
		job_conf = parse(filename)

		#-----UML balise creation----------------------------------------------------------------#
		tools = job_conf.getElementsByTagName("tools")[0]

		for name in self.lbases :
			locals()["tool_%s" % name] = job_conf.createElement("tool")
			locals()["tool_%s" % name].setAttribute("id","%s_%s" % (name,self.P.lower()))
			locals()["tool_%s" % name].setAttribute("destination", "blast_destinate") #TODO : Fix the newline
			tools.appendChild(locals()["tool_%s" % name])		
		#----------------------------------------------------------------------------------------#

		outfd = codecs.open(filename,"w","utf-8")
		job_conf.writexml(outfd,addindent="\t",newl="\n")
		outfd.close()
		rmblank(filename)
		fixparam(filename)

		if self.v : print "Update job_conf : Done."

#----------------------------------------------------------------------------------------#	
def remove_user(id_group,id_user):
	
	"""
	Remove a user from a group
	"""
	i = GalaxyInstance(URL,APIKEY)
	gc = GroupsClient(i)
	
	payload = {}
	url = "http://%s/api/groups/%s/users/%s" % (URL,id_group,id_user)

	Client._delete(gc, payload, url = url)

#----------------------------------------------------------------------------------------#	
def add_user(id_group, project_name, id_user):
	
	"""
	Add a user to a group
	"""
	i = GalaxyInstance(URL,APIKEY)
	gc = GroupsClient(i)

	url="http://%s/api/groups/%s" % (URL, id_group)
	payload = {}
	payload['name'] = "G_" + project_name
	payload['user_ids'] = [id_user]
	payload['role_ids'] = []

	Client._put(gc, payload, url = url)

#----------------------------------------------------------------------------------------#	
def rmblank(filename):
	
	"""
	Remove blank line in a file
	"""

	f = open(filename,"r")
	filtered = filter(lambda x: not re.match(r'^\s*$', x), f)
	f.close()

	f = open(filename,"w")
	for l in filtered : f.write(l)
	f.close()

def fixparam(filename):
	
	"""
	Fix abusive layout around param tags in XML file (job_conf)
	"""
	File = os.popen("sed -e '/blast_rules/,+1d' %s | sed 's/<param id=\"function\">/<param id=\"function\">blast_rules<\/param>/g' " % filename).read()
	os.popen("echo '%s' > %s" % (File,filename))

##########################################################################################

if __name__ == "__main__":

	#--------Get Arguments in Command line---------------------------------------------------#
	parser = argparse.ArgumentParser()

	parser.add_argument('-n',"--name", help="Project Name for a Blast tool", action='store')
	
	action = parser.add_mutually_exclusive_group(required=True)
	action.add_argument('-p', '--addproject', help="Add a New project", action='store_true')
	action.add_argument('-a', '--addusers', help="Add users to a group", action='store_true')
	action.add_argument('-r', '--removeusers', help="Remove users to a group", action='store_true')
	action.add_argument('-s', '--showusers', help="Show users in a group", action='store_true')
	action.add_argument('-S', '--showproject', help="Show all project's names", action='store_true')

	parser.add_argument("--users", help="List of Users logins separated by commas", action='store')
	parser.add_argument("--domain", help="Domain of users mails", action='store', default='sb-roscoff.fr')
	parser.add_argument("--url", help="Galaxy instance URL", action='store')
	parser.add_argument("--key", help="Admin Api Key of galaxy instance", action='store')
	parser.add_argument("-v", help="Verbose/Debug mode", action='store_true')
	
	args = parser.parse_args()
	#----------------------------------------------------------------------------------------#

	if (args.addusers or args.removeusers or args.showusers or args.addproject) and not args.name :
		parser.error('argument -n/--name is required')

	#--------Existing Project----------------------------------------------------------------#
	url="http://%s/api/groups/" % URL
	dic_groups = requests.get(url, verify=False, params={'key': APIKEY})
	PROJECTLIST = map(lambda x : str(x['name']), dic_groups.json())
	PROJECTLIST = [i[2:] for i in PROJECTLIST if i.startswith("G_")]
	if args.v or args.showproject: print "PROJECTLIST = ", PROJECTLIST
	#----------------------------------------------------------------------------------------#

	#--------Existing Users------------------------------------------------------------------#
	url="http://%s/api/users/" % URL
	dic_users = requests.get(url, verify=False, params={'key': APIKEY})
	USERLIST = dict(map(lambda x : (str(x["email"]), str(x["id"])) , dic_users.json()))
	if args.v : print "USERLIST = ", USERLIST.keys()
	#----------------------------------------------------------------------------------------#

	#--------Args control--------------------------------------------------------------------#
	## Control project's name :
	if args.addproject and args.name.capitalize() in PROJECTLIST :
		parser.error('The name "%s" is already use for a project' % args.name)
		pass
	elif (args.addusers or args.removeusers or args.showusers) and args.name.capitalize() not in PROJECTLIST :
		parser.error('The project "%s" does not exist' % args.name)

	## Get users in group :
	if args.removeusers or args.addusers or args.showusers:
			id_group = [dic["id"] for dic in dic_groups.json() if dic["name"] == "G_" + args.name][0]
			url="http://%s/api/groups/%s/users" % (URL,id_group)
			dic_users_group = requests.get(url, verify=False, params={'key': APIKEY})
			USERGROUPLIST = dict(map(lambda x : (str(x["email"]), str(x["id"])) , dic_users_group.json()))
			if args.v or args.showusers: print "USERGROUPLIST = ", USERGROUPLIST.keys()

	## Control args number :
	if args.addproject or args.removeusers or args.addusers :
		if not args.users :
			parser.error('Enter at least one User Login (separated by commas)')
		if not args.domain and args.do != 'R' or not re.match('^[a-z_\-]+\.[a-z]{2,3}$',args.domain):
			parser.error('Enter a valid domain name ex : sb-roscoff.fr')	

		UsersList = args.users.split(",")
		UsersList = map(lambda x : x+'@'+args.domain, UsersList)
		if args.v : print "EnteredUsersList = ", UsersList

		## Control users'name - Existing :
		USERS = USERLIST.keys()
		for user in UsersList :
			if user not in USERS :
				print "User %s does not exist. Add a count in galaxy" % user
				UsersList.remove(user)
				continue
			
			if args.removeusers :
				if user in USERGROUPLIST : remove_user(id_group, USERGROUPLIST[user])
				else : print "User %s not in %s. Undeletable." % (user, args.name)

			elif args.addusers :
				if user not in USERGROUPLIST : add_user(id_group, args.name, USERLIST[user])
				else : print "User %s already in %s." % (user, args.name)
	#----------------------------------------------------------------------------------------#

	## Project Creation
	if args.addproject and UsersList != [] : 
		P = ProjectBlast(ProjectName = args.name, UsersList = map(lambda x : USERLIST[x], UsersList ), verbose = args.v)

		
		
		


