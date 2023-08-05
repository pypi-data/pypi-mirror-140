import json
from .BaseObject import BaseObject
class TyposquatDomain(BaseObject):
  def __init__(self, api_key):
    BaseObject.__init__(self, api_key)
    self.added_at = None
    self.domain = None
    self.last_scanned_at = None
    self.num_registered = None
    self.num_unregistered = None
    self.primary_domain = None
  def from_dict(self, d):
    if 'added_at' in d:
      self.added_at = d['added_at']
    if 'domain' in d:
      self.domain = d['domain']
    if 'last_scanned_at' in d:
      self.last_scanned_at = d['last_scanned_at']
    if 'num_registered' in d:
      self.num_registered = d['num_registered']
    if 'num_unregistered' in d:
      self.num_unregistered = d['num_unregistered']
    if 'primary_domain' in d:
      self.primary_domain = d['primary_domain']
  def to_dict(self):
    d = {}
    d['added_at'] = self.added_at
    d['domain'] = self.domain
    d['last_scanned_at'] = self.last_scanned_at
    d['num_registered'] = self.num_registered
    d['num_unregistered'] = self.num_unregistered
    d['primary_domain'] = self.primary_domain
    return d
  def to_json(self):
    d = self.to_dict()
    return json.dumps(d)
