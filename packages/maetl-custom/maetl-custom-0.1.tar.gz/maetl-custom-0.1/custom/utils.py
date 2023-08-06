import os
import hashlib

def upload_files(instance, filename):
	upload_to = 'project_letters/{}/'.format(instance.project_letter.project.project_code)
	number = instance.project_letter.number.replace("/", "-")
	field = 'files'
	ext = filename.split('.')[-1]
	if instance.pk:
		filename = '{}_{}_{}_{}.{}'.format(field,instance.project_letter.letter_date,number,instance.pk, ext)
	else:
		filename = '{}.{}'.format(uuid4().hex, ext)
	return os.path.join(upload_to, filename)


def getnewid(table_name):
	result = table_name.objects.last()
	if result:
		newid = result.id + 1
		hashid = hashlib.md5(str(newid).encode())
	else:
		newid = 1
		hashid = hashlib.md5(str(newid).encode())
	return newid, hashid.hexdigest()

def getjustnewid(table_name):
	result = table_name.objects.last()
	if result:
		newid = result.id + 1
	else:
		newid = 1
	return newid
	 
def onlygetnewid(table_name):
	result = table_name.objects.latest("id")
	if result:
		newid = result.id + 1
	else:
		newid = 1
	return newid

def getlastid(table_name):
	result = table_name.objects.last()
	if result:
		lastid = result.id
		newid = lastid + 1
	else:
		lastid = 0
		newid = 1
	return lastid, newid

def hash_md5(strhash):
	hashed = hashlib.md5(strhash.encode())
	return hashed.hexdigest()
