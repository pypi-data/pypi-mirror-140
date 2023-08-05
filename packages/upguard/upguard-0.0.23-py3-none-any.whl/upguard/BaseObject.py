import requests
import json
import urllib3
class BaseObject:
  def from_dict(self, d):
    if 'api_key' in d:
      self.api_key = d['api_key']
  def to_dict(self):
    d = {}
    d['api_key'] = self.api_key
    return d
  def to_json(self):
    d = self.to_dict()
    return json.dumps(d)
    
  def __init__(self, api_key):
    self.api_key = api_key
  

    
  def make_headers(self):
    return {
      'Authorization': self.api_key,
      'Content-Type': 'application/json'
    }
  

    
  def http_get(self, path):
    url = str(path)
    headers = self.make_headers()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      raise Exception(str(response.status_code) + ":" + response.text)
    return response.json()
  

    
  def http_get_raw(self, path):
    url = str(path)
    headers = self.make_headers()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      raise Exception(str(response.status_code) + ":" + response.text)
    return response.content
  

