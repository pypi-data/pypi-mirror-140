import json
from .BaseObject import BaseObject
from .QuestionnaireList import QuestionnaireList
from .Questionnaire import Questionnaire
from .VulnerabilityList import VulnerabilityList
from .Vulnerability import Vulnerability
class Vendor(BaseObject):
  def __init__(self, api_key):
    BaseObject.__init__(self, api_key)
    self.automated_score = None
    self.brand_protection_score = None
    self.email_security_score = None
    self.id = None
    self.industry_group = None
    self.industry_sector = None
    self.labels = []
    self.name = None
    self.network_security_score = None
    self.overall_score = None
    self.phishing_score = None
    self.primary_domain = None
    self.questionnaire_score = None
    self.tier = None
    self.website_security_score = None
  def from_dict(self, d):
    if 'automated_score' in d:
      self.automated_score = d['automated_score']
    if 'brand_protection_score' in d:
      self.brand_protection_score = d['brand_protection_score']
    if 'email_security_score' in d:
      self.email_security_score = d['email_security_score']
    if 'id' in d:
      self.id = d['id']
    if 'industry_group' in d:
      self.industry_group = d['industry_group']
    if 'industry_sector' in d:
      self.industry_sector = d['industry_sector']
    if 'labels' in d:
      self.labels = d['labels']
    if 'name' in d:
      self.name = d['name']
    if 'network_security_score' in d:
      self.network_security_score = d['network_security_score']
    if 'overall_score' in d:
      self.overall_score = d['overall_score']
    if 'phishing_score' in d:
      self.phishing_score = d['phishing_score']
    if 'primary_domain' in d:
      self.primary_domain = d['primary_domain']
    if 'questionnaire_score' in d:
      self.questionnaire_score = d['questionnaire_score']
    if 'tier' in d:
      self.tier = d['tier']
    if 'website_security_score' in d:
      self.website_security_score = d['website_security_score']
  def to_dict(self):
    d = {}
    d['automated_score'] = self.automated_score
    d['brand_protection_score'] = self.brand_protection_score
    d['email_security_score'] = self.email_security_score
    d['id'] = self.id
    d['industry_group'] = self.industry_group
    d['industry_sector'] = self.industry_sector
    d['labels'] = self.labels
    d['name'] = self.name
    d['network_security_score'] = self.network_security_score
    d['overall_score'] = self.overall_score
    d['phishing_score'] = self.phishing_score
    d['primary_domain'] = self.primary_domain
    d['questionnaire_score'] = self.questionnaire_score
    d['tier'] = self.tier
    d['website_security_score'] = self.website_security_score
    return d
  def to_json(self):
    d = self.to_dict()
    return json.dumps(d)
    
  def questionnaires(self):
    url = "https://cyber-risk.upguard.com/api/public/vendor/questionnaires?vendor_primary_hostname=" + str(self.primary_domain) + ""
    obj = self.http_get(url)
    the_list = QuestionnaireList(self.api_key)
    for x in obj["questionnaires"]:
      elem = Questionnaire(self.api_key)
      if "sent_at" in x:
        elem.sent_at = x["sent_at"]
      if "status" in x:
        elem.status = x["status"]
      if "id" in x:
        elem.id = x["id"]
      if "name" in x:
        elem.name = x["name"]
      if "returned_at" in x:
        elem.returned_at = x["returned_at"]
      the_list.append(elem)
    return the_list
  

    
  def vulnerabilities(self):
    url = "https://cyber-risk.upguard.com/api/public/vulnerabilities/vendor?primary_hostname=" + str(self.primary_domain) + ""
    obj = self.http_get(url)
    the_list = VulnerabilityList(self.api_key)
    for x in obj["vulnerabilities"]:
      elem = Vulnerability(self.api_key)
      if "cve" in x:
        if "severity" in x["cve"]:
          elem.cve_severity = x["cve"]["severity"]
      if "hostname" in x:
        elem.domain = x["hostname"]
      if "ip_addresses" in x:
        elem.ip_addresses = x["ip_addresses"]
      if "verified" in x:
        elem.verified = x["verified"]
      if "cpes" in x:
        elem.cpes = x["cpes"]
      if "created_at" in x:
        elem.created_at = x["created_at"]
      if "cve" in x:
        if "description" in x["cve"]:
          elem.cve_description = x["cve"]["description"]
      if "cve" in x:
        if "id" in x["cve"]:
          elem.cve_id = x["cve"]["id"]
      the_list.append(elem)
    return the_list
  

