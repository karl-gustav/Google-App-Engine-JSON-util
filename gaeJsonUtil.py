from google.appengine.ext.db import Model, Key
from google.appengine.api.users import User
import json
import logging
from cgi import escape as htmlEscape
from datetime import datetime

KEY_IDENTIFIER = "id"

def modelListToJson(lst):
	out = []
	for item in lst:
		if isinstance(item, Model):
			out.append(modelToJson(item))
		else:
			out.append(json.dumps(item))
	return "[%s]" % ",".join(out)
	
def modelToJson(obj):
	tempdict = {}
	for key in obj.properties():
		value = getattr(obj, key)
		tempdict[key] = makeJsonSafe(value)

	tempdict[KEY_IDENTIFIER] = unicode(obj.key())
	jsonString = json.dumps(tempdict)

	return jsonString
	
def jsonToModel(clazz, jsonString, existingInstanceKey=None):
	jsonObj = json.loads(jsonString)
	if existingInstanceKey:
		if jsonObj.has_key(KEY_IDENTIFIER):
			if existingInstanceKey.lower() != jsonObj[KEY_IDENTIFIER].lower():
				raise Exception("JSON %s don't match the one in the URL!" % KEY_IDENTIFIER)
		instance = clazz.get(existingInstanceKey)
	else:
		if jsonObj.has_key(KEY_IDENTIFIER):
			raise Exception("Json can't contain id when it supose to be a new object!")
		instance = clazz()
		
	for property, value in jsonObj.items():
		if hasattr(clazz, property):
			value = convertToGaeDatatype(instance, property, value)
			setattr(instance, property, value)
		else:
			if property != KEY_IDENTIFIER:
				logging.info('Ignored the "%s" property not found on the %s class' % (property, clazz.__name__))

		
	return instance

def convertToGaeDatatype(inst, property, value):
	if isinstance(getattr(inst,property), datetime): #2014-10-11 08:23:16.114669
		return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
	elif isinstance(getattr(inst,property), User):
		return User(value)
	elif isinstance(getattr(inst,property), Model):
		return Key(value)
	elif isinstance(getattr(inst,property), str):
		return htmlEscape(value)
	else:
		return value

def makeJsonSafe(value):
	if isinstance(value, Model):
		return unicode(value.key())
	elif isinstance(value, list):
		return [makeJsonSafe(x) for x in value]
	elif isinstance(value, (int, long, float, complex)):
		return value
	elif isinstance(value, bool):
		return value
	else:
		return unicode(value)

