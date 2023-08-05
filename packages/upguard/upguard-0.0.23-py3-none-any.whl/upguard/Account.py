import json
from .BaseObject import BaseObject
from .VendorList import VendorList
from .Vendor import Vendor
from .VulnerabilityList import VulnerabilityList
from .Vulnerability import Vulnerability
class Account(BaseObject):
    
  def monitor_vendor(self, hostname):
    url = "https://cyber-risk.upguard.com/api/public/vendor?hostname=" + str(hostname) + "&start_monitoring=true"
    obj = self.http_get(url)
    elem = Vendor(self.api_key)
    if "name" in obj:
      elem.name = obj["name"]
    if "overallScore" in obj:
      elem.overall_score = obj["overallScore"]
    if "primary_hostname" in obj:
      elem.primary_domain = obj["primary_hostname"]
    if "automatedScore" in obj:
      elem.automated_score = obj["automatedScore"]
    if "categoryScores" in obj:
      if "brandProtection" in obj["categoryScores"]:
        elem.brand_protection_score = obj["categoryScores"]["brandProtection"]
    if "categoryScores" in obj:
      if "networkSecurity" in obj["categoryScores"]:
        elem.network_security_score = obj["categoryScores"]["networkSecurity"]
    if "categoryScores" in obj:
      if "phishing" in obj["categoryScores"]:
        elem.phishing_score = obj["categoryScores"]["phishing"]
    if "industry_sector" in obj:
      elem.industry_sector = obj["industry_sector"]
    if "categoryScores" in obj:
      if "emailSecurity" in obj["categoryScores"]:
        elem.email_security_score = obj["categoryScores"]["emailSecurity"]
    if "categoryScores" in obj:
      if "websiteSecurity" in obj["categoryScores"]:
        elem.website_security_score = obj["categoryScores"]["websiteSecurity"]
    if "id" in obj:
      elem.id = obj["id"]
    if "industry_group" in obj:
      elem.industry_group = obj["industry_group"]
    if "questionnaireScore" in obj:
      elem.questionnaire_score = obj["questionnaireScore"]
    return elem
  

    
  def typoquat_domains(self):
    obj = self.http_get("https://cyber-risk.upguard.com/api/public/typosquat")
    the_list = TyposquatDomainList(self.api_key)
    for x in obj["domains"]:
      elem = TyposquatDomain(self.api_key)
      if "num_registered" in x:
        elem.num_registered = x["num_registered"]
      if "num_unregistered" in x:
        elem.num_unregistered = x["num_unregistered"]
      if "primary_domain" in x:
        elem.primary_domain = x["primary_domain"]
      if "added_at" in x:
        elem.added_at = x["added_at"]
      if "domain" in x:
        elem.domain = x["domain"]
      if "last_scanned_at" in x:
        elem.last_scanned_at = x["last_scanned_at"]
      the_list.append(elem)
    return the_list
  

    
  def vendors(self):
    next_page_token = None
    the_list = VendorList(self.api_key)
    while True:
      url = "https://cyber-risk.upguard.com/api/public/vendors"
      if next_page_token != None:
        url += "&page_token=" + next_page_token
      obj = self.http_get(url)
      if len(obj["vendors"]) == 0:
        break
      for x in obj["vendors"]:
        elem = Vendor(self.api_key)
        if "automatedScore" in x:
          elem.automated_score = x["automatedScore"]
        if "category_scores" in x:
          if "websiteSecurity" in x["category_scores"]:
            elem.website_security_score = x["category_scores"]["websiteSecurity"]
        if "id" in x:
          elem.id = x["id"]
        if "monitored" in x:
          elem.monitored = x["monitored"]
        if "overallScore" in x:
          elem.overall_score = x["overallScore"]
        if "primary_hostname" in x:
          elem.primary_domain = x["primary_hostname"]
        if "questionnaireScore" in x:
          elem.questionnaire_score = x["questionnaireScore"]
        if "category_scores" in x:
          if "emailSecurity" in x["category_scores"]:
            elem.email_security_score = x["category_scores"]["emailSecurity"]
        if "labels" in x:
          elem.labels = x["labels"]
        if "name" in x:
          elem.name = x["name"]
        if "tier" in x:
          elem.tier = x["tier"]
        if "category_scores" in x:
          if "brandProtection" in x["category_scores"]:
            elem.brand_protection_score = x["category_scores"]["brandProtection"]
        if "category_scores" in x:
          if "networkSecurity" in x["category_scores"]:
            elem.network_security_score = x["category_scores"]["networkSecurity"]
        if "category_scores" in x:
          if "phishing" in x["category_scores"]:
            elem.phishing_score = x["category_scores"]["phishing"]
        the_list.append(elem)
      if "next_page_token" in obj:
        next_page_token = obj["next_page_token"]
      else:
        break
    return the_list
  

    
  def vendor_by_domain(self, hostname):
    url = "https://cyber-risk.upguard.com/api/public/vendor?hostname=" + str(hostname) + "&"
    obj = self.http_get(url)
    elem = Vendor(self.api_key)
    if "id" in obj:
      elem.id = obj["id"]
    if "overallScore" in obj:
      elem.overall_score = obj["overallScore"]
    if "questionnaireScore" in obj:
      elem.questionnaire_score = obj["questionnaireScore"]
    if "categoryScores" in obj:
      if "websiteSecurity" in obj["categoryScores"]:
        elem.website_security_score = obj["categoryScores"]["websiteSecurity"]
    if "industry_group" in obj:
      elem.industry_group = obj["industry_group"]
    if "industry_sector" in obj:
      elem.industry_sector = obj["industry_sector"]
    if "automatedScore" in obj:
      elem.automated_score = obj["automatedScore"]
    if "categoryScores" in obj:
      if "brandProtection" in obj["categoryScores"]:
        elem.brand_protection_score = obj["categoryScores"]["brandProtection"]
    if "categoryScores" in obj:
      if "emailSecurity" in obj["categoryScores"]:
        elem.email_security_score = obj["categoryScores"]["emailSecurity"]
    if "categoryScores" in obj:
      if "networkSecurity" in obj["categoryScores"]:
        elem.network_security_score = obj["categoryScores"]["networkSecurity"]
    if "categoryScores" in obj:
      if "phishing" in obj["categoryScores"]:
        elem.phishing_score = obj["categoryScores"]["phishing"]
    if "name" in obj:
      elem.name = obj["name"]
    if "primary_hostname" in obj:
      elem.primary_domain = obj["primary_hostname"]
    return elem
  

