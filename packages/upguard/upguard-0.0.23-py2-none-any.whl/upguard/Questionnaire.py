import json
from .BaseObject import BaseObject
from .QuestionnaireAttachmentList import QuestionnaireAttachmentList
from .QuestionnaireAttachment import QuestionnaireAttachment
class Questionnaire(BaseObject):
  def __init__(self, api_key):
    BaseObject.__init__(self, api_key)
    self.id = None
    self.name = None
    self.returned_at = None
    self.sent_at = None
    self.status = None
  def from_dict(self, d):
    if 'id' in d:
      self.id = d['id']
    if 'name' in d:
      self.name = d['name']
    if 'returned_at' in d:
      self.returned_at = d['returned_at']
    if 'sent_at' in d:
      self.sent_at = d['sent_at']
    if 'status' in d:
      self.status = d['status']
  def to_dict(self):
    d = {}
    d['id'] = self.id
    d['name'] = self.name
    d['returned_at'] = self.returned_at
    d['sent_at'] = self.sent_at
    d['status'] = self.status
    return d
  def to_json(self):
    d = self.to_dict()
    return json.dumps(d)
    
  def attachments(self):
    url = "https://cyber-risk.upguard.com/api/public/vendor/questionnaire/attachment/list?questionnaire_id=" + str(self.id) + ""
    obj = self.http_get(url)
    the_list = QuestionnaireAttachmentList(self.api_key)
    for x in obj["attachments"]:
      elem = QuestionnaireAttachment(self.api_key)
      if "description" in x:
        elem.description = x["description"]
      if "file_name" in x:
        elem.file_name = x["file_name"]
      if "id" in x:
        elem.id = x["id"]
      if "uploaded_at" in x:
        elem.uploaded_at = x["uploaded_at"]
      the_list.append(elem)
    return the_list
  

