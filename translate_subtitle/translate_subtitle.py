#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import os
import time
import pysrt
import shutil
from selenium import webdriver


# Translate Subtitle ver1.1
# PARAMETER ==========================================================================================================
target_path = "/Users/..."

# language combination
input_lang, output_lang = "en", "ja" # you can find language notation from url.

dual_subtitle = True

make_backup_folder = True
backup_folder = "_backup"
# -------------------------------------------------------------------------------------------------------------------
limit_amount = 4000 #avoid maximum word limit
selenium_path = "/Applications/chromedriver" # mac os application path
url = "https://translate.google.com/#view=home&op=translate&sl={}&tl={}&text=.".format(input_lang, output_lang)
# ====================================================================================================================


class TranslationSRT():
	# ver1.1
	def __init__(self):

		self.driver = webdriver.Chrome(selenium_path)

	def open_page(self):

		self.driver.get(url)

	def close(self):

		self.driver.close()

	def translate(self, text):

		self.driver.get(url)

		element = self.driver.find_element_by_xpath('//*[@id="source"]')
		self.driver.execute_script("arguments[0].value=arguments[1]", element, text)
		time.sleep(3) #avoid connection delay
		result = self.driver.find_element_by_xpath('//*[@class="tlid-translation translation"]').text

		return result

def find_all_file(path, ignore_folder):
	# ver1.0
	for root, dirs, files in os.walk(path):
		yield root
		if root.find(ignore_folder) == -1:
			for file in files:
				yield os.path.join(root, file)


if dual_subtitle:
	suffix = "_{}-{}".format(input_lang, output_lang)
else:
	suffix = "_{}".format(output_lang)

list_srt = []
for full_path in find_all_file(target_path, backup_folder):
	split_full_path = os.path.split(full_path)
	file_path, file_name = split_full_path[0], split_full_path[1]
	if file_name.find(".srt") != -1 and file_name.find(suffix) == -1:
		list_srt.append({"name": file_name, "path": file_path})

if len(list_srt) != 0:

	if make_backup_folder:
		backup_path = os.path.join(target_path, backup_folder)
		if not os.path.exists(backup_path):
			os.mkdir(backup_path)
	else:
		backup_path = target_path

	print("[ APP ] Launching Selenium Chrome...\n", flush= True)

	app = TranslationSRT()
	app.open_page()

	count_loop = 0
	for srt in list_srt:
		count_loop += 1

		print("[ PROCESS ] Translating... {}/{}  {}".format(count_loop, len(list_srt), srt["name"]), flush= True)

		# translate
		input_srt = pysrt.open(os.path.join(srt["path"], srt["name"]))

		input_subtitle = []
		for line in input_srt:
			line_string = line.text.replace("\n", " ")
			if line_string.strip() == "":
				line_string = "-"
			input_subtitle.append(line_string)

		#avoid maximum word limit
		stock, output_srt = "", ""
		count_limit = 0
		for subtitle in input_subtitle:
			if count_limit + len(subtitle) < limit_amount:
				count_limit += len(subtitle)
				stock += subtitle + "\n"
			else:
				output_srt += app.translate(stock) + "\n"
				count_limit = 0
				count_limit += len(subtitle)
				stock = ""
				stock += subtitle + "\n"

		if len(stock) != 0:
			output_srt += app.translate(stock) + "\n"

		output_srt = output_srt.split("\n")

		for index, subtitle in enumerate(input_srt):
			subtext_input = input_subtitle[index]
			subtext_output = output_srt[index]

			if dual_subtitle:
				subtitle.text = subtext_input + "\n" + subtext_output
			else:
				subtitle.text = subtext_output

		# backup
		if make_backup_folder:
			shutil.move(os.path.join(srt["path"], srt["name"]), os.path.join(backup_path, srt["name"]))
		# generate
		split_file_name = srt["name"].split(".")
		input_srt.save(os.path.join(srt["path"], split_file_name[0] + suffix + "." + split_file_name[1]), "utf-8")

	app.close()
	print("\n[ APP ] Finish. Translated and generated new srt file.")
else:
	print("[ ERROR ] No srt file.")
