# jianshou-client
Jianshou Client APIs

```bash
# Install a virtual environment
pipenv shell
```
# Install the dependencies in setup.py
`pipenv install -e .`

## Installation
```bash
pip install jianshou-client
```

## Usage
Import the package
```python
from jianshou import JianshouClient
```

Create an instance of `jianshou-client`
```python
from dotenv import load_dotenv
from jianshou import JianshouClient
# Create a `.env` file to load environmental variables
load_dotenv()

# Use the environmental variables or read them from inputs
JIANSHOU_EMAIL = os.environ.get('JIANSHOU_EMAIL') or input("Jianshou email: ")
JIANSHOU_PASSWD = os.environ.get('JIANSHOU_PASSWD') or input("Jianshou password: ")
jianshou_client = JianshouClient(JIANSHOU_EMAIL, JIANSHOU_PASSWD)
```

Upload an item for sale
```python
item = jianshou_client.upload(name="new item", intro='testing', content="testing")
hashid = item.hashid
```

Delete an item
```python
hashid = "123456"
item = jianshou_client.delete(hashid)
```

Update item base info and pay info
```python
hashid = "123456"
updated_item = jianshou_client.update_baseinfo(hashid, new_name="new_item_updated", new_intro="intro_updated")
updated_item = jianshou_client.update_payinfo(hashid, new_price=111, new_stock=111, new_content="hello")
```

Generate a html snippet to be embeded in base info content or pay info content
```python
# A paragraph of text followed by external links and images.
html_snippet = gen_typical_html_snippet(
	"one paragraph", 
	other_links=["https://www.google.com"],
	image_links=["https://yourdomain.com/path/to/directlink/photo.jpg"]
)
```