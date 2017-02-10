import requests
from bs4 import BeautifulSoup
import locale
import json
import csv

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )

print("\n\nGetting User Page\n\n")
page = requests.get("https://www.fanfiction.net/u/2583361/")
print("\n\nGetting User Page - Completed\n\n")
# page.content = page.content.encode('utf-8')
soup = BeautifulSoup(page.content, 'html.parser')
fav_stories_div = soup.find_all('div', class_='z-list favstories')
stories_metadata = []

for n, story in enumerate(fav_stories_div):
	story_elements = list(story.children)
	desc_with_metadata = str(story.find_all('div', class_='z-indent z-padtop')[0])
	desc_metadata = str(story.find_all('div', class_='z-indent z-padtop')[0].find_all('div', class_="z-padtop2 xgray")[0])
	desc_metadata_soup = story.find_all('div', class_='z-indent z-padtop')[0].find_all('div', class_="z-padtop2 xgray")[0]
	desc_without_metadata = desc_with_metadata.replace(desc_metadata, "")
	desc_without_metadata_soup = BeautifulSoup(desc_without_metadata, 'html.parser')
	desc_metadata_list = [x.strip() for x in desc_metadata_soup.get_text().split(' - ')]

	story_metadata = {
		"story_name": story_elements[0].get_text(),
		"story_start_url_relative": story_elements[0].get('href'),
		"story_end_url_relative": story_elements[2].get('href'),
		"author_name": story_elements[4].get_text(),
		"author_url_relative": story_elements[4].get('href'),
		"reviews_url_relative": story.find_all('a', class_='reviews')[0].get('href'),
		"story_summary": desc_without_metadata_soup.get_text()
	}

	if "Crossover" in desc_metadata_list[0]:
		del desc_metadata_list[0]
		story_metadata = merge_two_dicts(story_metadata, {
			"story_crossover": "Y",
			"story_parent": desc_metadata_list[0].split(' & ')
		})
	else:
		story_metadata = merge_two_dicts(story_metadata, {
			"story_crossover": "N",
			"story_parent": [desc_metadata_list[0]]
		})
	if "Chapters" in desc_metadata_list[3]:
		desc_metadata_list.insert(3, "Unknown")
	if "Published" in desc_metadata_list[9]:
		desc_metadata_list.insert(9, "Updated: Unknown")
	if "Complete" == desc_metadata_list[-1]:
		del desc_metadata_list[-1]
		story_metadata = merge_two_dicts(story_metadata, {
			"story_complete": "Y"
		})
	else:
		story_metadata = merge_two_dicts(story_metadata, {
			"story_complete": "N"
		})
	if "Published" in desc_metadata_list[-1]:
		desc_metadata_list.append("Unknown")

	if len(desc_metadata_list) == 12:
		try:
			desc_metadata_dict = {
				"story_parent": desc_metadata_list[0],
				"story_rating": desc_metadata_list[1].split(': ')[1],
				"story_language": desc_metadata_list[2],
				"story_genre": desc_metadata_list[3],
				"story_chapter_count": desc_metadata_list[4].split(': ')[1],
				"story_word_count": locale.atoi(desc_metadata_list[5].split(': ')[1]),
				"story_review_count": desc_metadata_list[6].split(': ')[1],
				"story_favourite_count": locale.atoi(desc_metadata_list[7].split(': ')[1]),
				"story_follow_count": locale.atoi(desc_metadata_list[8].split(': ')[1]),
				"story_last_updated_date": desc_metadata_list[9].split(': ')[1],
				"story_published_date": desc_metadata_list[10].split(': ')[1],
				"story_main_characters": desc_metadata_list[11].split(', ')
			}
		except IndexError as e:
			print e, len(desc_metadata_list), story_metadata, desc_metadata_list
			break
		story_metadata = merge_two_dicts(story_metadata, desc_metadata_dict)
	else:
		print len(desc_metadata_list), story_metadata, desc_metadata_list
	stories_metadata.append(story_metadata)

with open('fav_stories_metadata.json', 'w') as outfile_json:
    json.dump(stories_metadata, outfile_json)
