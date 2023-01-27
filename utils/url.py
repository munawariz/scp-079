import urllib.parse
import urllib.error
import urllib.request

def is_valid_image(url):
    valid_exts = ['jpg', 'jpeg', 'png', 'webm', 'gif']
    parsed = urllib.parse.urlparse(url)
    ext = parsed.path.split('.')[-1]

    if ext.lower() in valid_exts:
        try:
            # Try to open the url
            urllib.request.urlopen(url)
            return True
        except urllib.error.HTTPError:
            return False
    else:
        return False