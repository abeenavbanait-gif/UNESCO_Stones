from bs4 import BeautifulSoup
import re

with open("site_703.html") as f:
    soup = BeautifulSoup(f, "html.parser")

headings = soup.find_all(re.compile('^h[1-6]$'), string=re.compile('Outstanding Universal Value', re.I))
if headings:
    h = headings[0]
    next_node = h.find_next_sibling()
    if next_node and next_node.name == 'div' and 'rich-text' in next_node.get('class', []):
        print(len(next_node.get_text(separator="\n", strip=True)))
        print(next_node.get_text(separator="\n\n", strip=True)[:500])
else:
    print("Not found")
