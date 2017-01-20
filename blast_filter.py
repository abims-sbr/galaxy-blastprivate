import re

def generique_restrict_blast( context, tool ):
    """
	This tool filter will hide Blast tool of a project for non-project users.
	"""
    user = context.trans.user
    if re.match("^[t]?blast[xpn]_",tool.name.lower()) :
        for user_group in user.groups:
           if user_group.group.name == "G_%s" % tool.name.split("_")[1].capitalize():
               return True
        # not found to have the role, return false:
        return False
    else: return True
