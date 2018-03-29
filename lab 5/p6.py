import sys
from urllib import urlopen
from stripogram import html2text
from bs4 import BeautifulSoup

soup = BeautifulSoup(urlopen(sys.argv[1]).read(), "lxml")
for _ in soup.find_all('h1', {'class' : 'title_news_detail mb10'}):
	print _.text
for _ in soup.find_all('h2', {'class' : 'description'}):
	print _.text
for _ in soup.find_all('p', {'class' : 'Normal'}):
	print _.text
