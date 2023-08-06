import requests
url = "https://api.replstories.xyz/mod"

class init:
	def __init__(self, userid):  
		self.uid = userid
	
	def verify(self, username):
		res = requests.post(f"{url}/verify/{username}/{self.uid}")
		text = res.text()
		return text
	
	def unverify(self, username):
		res = requests.post(f"{url}/unverify/{username}/{self.uid}")
		text = res.text()
		return text

	def terminate(self, username):
		res = requests.post(f"{url}/terminate/{username}/${self.uid}")
		text = res.text()
		return text

	def unterminate(self, username):
		res = requests.post(f"{url}/unterminate/{username}/${self.uid}")
		text = res.text()
		return text