import requests
from bs4 import BeautifulSoup
from yattag import Doc

# The two main cookies used by jianshou.
# cookie = res.headers['Set-Cookie']
# cookie_dict = session.cookies.get_dict()
# print({
# 	"XSRF-TOKEN": cookie_dict['XSRF-TOKEN'],
# 	"pro_session": cookie_dict['pro_session']
# })

# The header is optional and jianshou APIs works fine without it.
# headers = {
# 	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
# 	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
# 	"Accept-Language": "en-US,en;q=0.5",
# 	"Accept-Encoding": "gzip, deflate, br",
# 	"Content-Type": "application/x-www-form-urlencoded",
# 	"Origin": "https://jianshou.online",
# 	"Connection": "keep-alive",
# 	"Upgrade-Insecure-Requests": "1",
# 	"Sec-Fetch-Dest": "document",
# 	"Sec-Fetch-Mode": "navigate",
# 	"Sec-Fetch-Site": "same-origin",
# 	"Sec-Fetch-User": "?1",
# 	"Sec-GPC": "1"
# }

class JianshouItem:
	def __init__(self, hashid, name=None, intro=None, content=None, price=None, stock=None):
		self.name = name
		self.intro = intro
		self.hashid = hashid
		self.content = content
		self.price = price
		self.stock = stock
		self.selling_link = f"https://jianshou.online/dashboard/snippet/{hashid}"

class JianshouClient:
	def __init__(self, email, passwd):
		if email is None or passwd is None:
			raise Exception("Email and password are required.")

		self.session = requests.Session()
		res = self.session.get('https://jianshou.online/login')
		html = res.content
		token = self._find_token(html)

		res = self.session.post('https://jianshou.online/login', data={
			'_token': token,
			'email': email, 
			'password': passwd
		})

		assert res.status_code == 200

		# Make sure the login is successful.
		if not self.is_logged_in():
			raise Exception("Login failed")

		# Find all items for sale and store them in a map.
		self.item_map = {}
		for item in self.find_items():
			self.item_map[item.hashid] = item
	
	def is_logged_in(self):
		res = self.session.get('https://jianshou.online/dashboard/snippet/index')
		html = res.content
		soup = BeautifulSoup(html, 'html.parser')
		tbodies = soup.find_all('tbody')
		if len(tbodies) == 0:
			return False
		else:
			return True

	def _find_token(self, html):
		soup = BeautifulSoup(html, 'html.parser')
		inputs = soup.find_all("input", attrs={"name": "_token"})
		if len(inputs) == 0:
			return None
		token = inputs[0]['value']
		return token

	# A paragraph of text followed by external links and images.
	def gen_typical_html_snippet(self, paragraph, image_links=[], other_links=[]):
		doc, tag, text = Doc().tagtext()
		with tag('p'):
			text(paragraph)
			if len(other_links) > 0:
				text("\nOther external links:\n")
				for link in other_links:
					with tag('p'):
						with tag('a', href=link):
							text(link)
		with tag('p'):
			if len(image_links) > 0:
				for link in image_links:
					doc.stag('img', src=link)

		html_snippet = doc.getvalue()
		return html_snippet

	def gen_video_html_snippet(self, video_link):
		doc, tag, text = Doc().tagtext()
		with tag('video', width="100%", height="100%", controls="controls"):
			doc.stag('source', src=video_link, type="video/mp4")
			with tag('p'):
				text("Video not supported by your browser.")
				with tag('a', href=video_link):
					text("Click here to open and download.")

		html_snippet = doc.getvalue()
		return html_snippet

	def refresh(self):
		new_item_map = {}
		for item in self.find_items():
			hashid = item.hashid
			new_item_map[hashid] = item
		self.item_map = new_item_map

	def find_items(self):
		items = []
		res = self.session.get('https://jianshou.online/dashboard/snippet/index')
		html = res.content
		soup = BeautifulSoup(html, 'html.parser')
		tbodies = soup.find_all('tbody')

		if len(tbodies) == 0:
			return []

		# Only hashid and name are available on index page
		tbody = tbodies[0]
		trs = tbody.find_all('tr')
		for tr in trs:
			tds = tr.find_all('td')
			hashid = tds[0].text.strip()
			name = tds[1].text.strip()
			# TODO: Add more properties
			item = JianshouItem(hashid, name=name)
			items.append(item)

		return items

	def upload(self, name=None, intro=None, content=None, price=1, stock=0):
		res = self.session.get('https://jianshou.online/dashboard/snippet/create')
		html = res.content
		token = self._find_token(html)

		data = {
			"_token": token,
			"name": name,
			"intro": intro,
			"type": "1",
			"content": content,
			"price": price,
			"stock": stock,
		}

		res = self.session.post('https://jianshou.online/dashboard/snippet/store', data=data)
		assert res.status_code == 200
		hashid = res.url.split('/')[-1]
		self.refresh()
		return self.item_map[hashid]

	def update_baseinfo(self, hashid, new_name=None, new_intro=None):
		if hashid not in self.item_map:
			print("Item not found by hashid %s" % hashid)
			return

		# TODO: Find name and intro from base info page
		baseinfo_url = format("https://jianshou.online/dashboard/snippet/%s/baseinfo" % hashid)
		res = self.session.get(baseinfo_url)
		html = res.content
		token = self._find_token(html)

		# The properties have to be set in the exact order below
		data = {
			"_method": "patch",
			"_token": token,
			"name": new_name if new_name else self.item_map[hashid].name,
			"intro": new_intro if new_intro else self.item_map[hashid].intro,
		}

		res = self.session.post(baseinfo_url, data=data)
		self.refresh()
		assert res.status_code == 200
		# print("Update basic info with status code: " + str(res.status_code))
		return self.item_map[hashid]

	def update_payinfo(self, hashid, new_price=None, new_stock=None, new_content=None):
		if hashid not in self.item_map:
			print("Item not found by hashid %s" % hashid)
			return

		# TODO: Find content, price and stock from pay info page
		payinfo_url = format("https://jianshou.online/dashboard/snippet/%s/payinfo" % hashid)
		res = self.session.get(payinfo_url)
		html = res.content
		token = self._find_token(html)

		# The properties have to be set in the exact order below
		data = {
			"_method": "patch",
			"_token": token,
			"content": new_content if new_content else self.item_map[hashid].content,
			# Price an stock cannot be None otherwise the request will fail.
			"price": str(new_price) if new_price else str(self.item_map[hashid].price or 1),
			# Note that if 0 equals if false
			"stock": str(new_stock) if new_stock or new_stock == 0 else str(self.item_map[hashid].stock or 0),
		}

		res = self.session.post(payinfo_url, data=data)
		self.refresh()
		assert res.status_code == 200
		# print("Update pay info with status code: " + str(res.status_code))
		return self.item_map[hashid]

	def delete(self, hashid):
		if hashid not in self.item_map:
			print("Item not found by hashid %s" % hashid)
			return

		deleted_item = self.item_map[hashid]
		resource_url = format("https://jianshou.online/dashboard/snippet/%s" % hashid)
		res = self.session.get(resource_url)
		html = res.content
		token = self._find_token(html)

		res = self.session.post(resource_url, data={
			'_token': token,
			'_method': 'delete',
		})

		self.refresh()
		assert res.status_code == 200
		return deleted_item