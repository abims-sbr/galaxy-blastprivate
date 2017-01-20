from galaxy.jobs.mapper import JobMappingException

def blast_rules(user, app, tool):
	# app is a galaxy.app.UniverseApplication object
	# user is a galaxy.model.User object or None
	# tool is a galaxy.tools.Tool object

	required_group = "G_%s" % tool.name.split('_')[-1].capitalize()
	# tool_id.capitalize()

	if user is None: raise JobMappingException('You must login to use this tool!')

	user_group_assocs = user.groups or []
	default_destination_id = app.job_config.get_destination(None)

	user_in_group = required_group in [user_group_assoc.group.name for user_group_assoc in user_group_assocs]
	
	if not user_in_group:
		raise JobMappingException('This tool is restricted to users in the %s group, please contact a site administrator to be authorized!' % required_group)

	else:
		return default_destination_id

