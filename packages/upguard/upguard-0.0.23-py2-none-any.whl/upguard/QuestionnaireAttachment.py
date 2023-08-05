import json
from .BaseObject import BaseObject
class QuestionnaireAttachment(BaseObject):
  def __init__(self, api_key):
    BaseObject.__init__(self, api_key)
    self.description = None
    self.file_name = None
    self.id = None
    self.uploaded_at = None
  def from_dict(self, d):
    if 'description' in d:
      self.description = d['description']
    if 'file_name' in d:
      self.file_name = d['file_name']
    if 'id' in d:
      self.id = d['id']
    if 'uploaded_at' in d:
      self.uploaded_at = d['uploaded_at']
  def to_dict(self):
    d = {}
    d['description'] = self.description
    d['file_name'] = self.file_name
    d['id'] = self.id
    d['uploaded_at'] = self.uploaded_at
    return d
  def to_json(self):
    d = self.to_dict()
    return json.dumps(d)
    
  def save_to_file(self):
    url = "https://cyber-risk.upguard.com/api/public/vendor/questionnaire/attachment?attachment_ids=" + str(self.id) + ""
    body = self.http_get_raw(url)
    f = open(self.file_name, "wb")
    f.write(body)
    f.close()
  

