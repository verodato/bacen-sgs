#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import re
import datetime
import html2text
import urllib
from lxml import html, etree
import requests
import string
from operator import itemgetter
import json
from shutil import copyfile
import os.path
import subprocess
import ssl
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import  urlparse, parse_qs
from pyvirtualdisplay import Display
import logging
from settings import path


def lastTimeUpdated(nome):
  ''' load historic series and get last date is was updated '''
  arq = path + 'csv/' + nome
  f = open( arq, 'r' )
  
  last = 0
  i = 0
  for line in f:
    if i > 0:
      l = line.split(';')
      # find last date
      last = l[0]
      last = datetime.datetime.strptime(last, '%d/%m/%Y')
    i += 1
  
  return last


def sgs( codigo, localFile ):
  ''' '''
  # check last time local file was updated
  nome = localFile
  last = lastTimeUpdated(nome)
  # next day
  nextDay = last + datetime.timedelta(days=1)
  dateIni = nextDay.strftime('%d%m%Y')
  
  # start webdriver and go to webpage
  display = Display(visible=0, size=(800, 800))  
  display.start()
  driver = webdriver.Chrome('/home/sander/chromedriver')  #ChromeDriverManager().install()
  driver.set_page_load_timeout(7) # sometimes page gets stuck
  url = 'https://www3.bcb.gov.br/sgspub/localizarseries/localizarSeries.do?method=prepararTelaLocalizarSeries'
  
  # date today
  t = time.localtime()
  today = time.strftime("%d%m%Y", t)
  day = time.strftime("%d", t)
  month = time.strftime("%m", t)
  year = time.strftime("%Y", t)
  
  # get url
  try:
    driver.get( url )
  except TimeoutException:
    pass
  
  # click OK on alert
  WebDriverWait(driver, 5).until(EC.alert_is_present())
  driver.switch_to.alert.accept()

  # "por codigo"
  xp = '//input[@id="txCodigo"]'
  e = driver.find_element_by_xpath( xp )
  e.send_keys( codigo )
  e.send_keys( Keys.ENTER )
  
  # iframe
  iframe = driver.find_element_by_xpath("//iframe[@id='iCorpo']")
  driver.switch_to.frame(iframe)
  
  # click checkbox
  xp = '//input[@name="cbxSelecionaSerie"]'
  e = driver.find_element_by_xpath( xp )
  e.click()
  
  # back from iframe
  #driver.switch_to.default_content()
  driver.switch_to.parent_frame()
  
  # click "search series"
  xp = '//*[@title="Search series"]'
  e = driver.find_element_by_xpath( xp )
  e.click()
  
  # wait until element to click is loaded
  wait = WebDriverWait(driver, 10)
  confirm = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dataInicio"]')))
  
  # choose initial date
  xp = '//*[@id="dataInicio"]'
  e = driver.find_element_by_xpath( xp )
  e.clear()
  e.send_keys( dateIni )
  
  # submit
  xp = '//*[@title="View values"]'
  e = driver.find_element_by_xpath( xp )
  e.click()
  
  # open file to append
  arq = path + 'csv/' + nome
  f = open( arq, 'a' )
  
  
  # scrapp table
  xp = '//*[@id="valoresSeries"]/tbody/tr'
  e = driver.find_elements_by_xpath( xp )
  
  for i in range(len( e )):
    if i > 2:
      line = re.sub('\n',';', e[ i ].text)
      if re.search('^[0-9]',line):
        print(line)
        f.write( line + '\n' )
  f.close
  
  time.sleep(5)
  
# RUN

if __name__ == "__main__":
  t = time.localtime()
  current_time = time.strftime("%H:%M:%S", t)
  today = time.strftime("%d%m%Y", t)
  print('Starting at ',current_time)
  # Taxa SML (real / peso argentino)
  codigo = '14001'
  localFile = 'pesos_argentinos.csv'
  sgs( codigo, localFile )
