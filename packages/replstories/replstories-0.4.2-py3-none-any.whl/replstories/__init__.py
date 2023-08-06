import requests
url = "https://api.replstories.xyz"

def getUser(username):
	res = requests.post(f"{url}/getuser?username={username}")
	json = res.json()
	return json

def getPost(username, postID):
	res = requests.post(f"{url}/getpost?username={username}&postid={postID}")
	json = res.json()
	return json

def getallPosts():
	res = requests.post(f"{url}/getallposts")
	json = res.json()
	return json

def getEntry(name):
	res = requests.post(f"{url}/getentry?name={name}")
	json = res.json()
	return json

def getallEntries():
	res = requests.post(f"{url}/getallentries")
	json = res.json()
	return json