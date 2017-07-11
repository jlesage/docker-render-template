#!/usr/bin/python3

import sys
import os
import argparse
import json
import collections
import xmltodict
import requests
from jinja2 import Environment, FileSystemLoader, BaseLoader

def dict_merge(dct, merge_dct):
  """
  Recursive dict merge. Inspired by :meth:``dict.update()``: instead of updating
  only top-level keys, dict_merge recurses down into dicts nested to an
  arbitrary depth, updating keys.  Lists are also merged together.
  The ``merge_dct`` is merged into ``dct``.
  :param dct: dict onto which the merge is executed
  :param merge_dct: dct merged into dct
  :return: None
  """
  for k, v in merge_dct.items():
    if (k in dct and isinstance(dct[k], dict)
          and isinstance(merge_dct[k], collections.Mapping)):
      dict_merge(dct[k], merge_dct[k])
    elif (k in dct and isinstance(dct[k], list)
          and isinstance(merge_dct[k], list)):
      # Merge list.
      dct[k] = dct[k] + merge_dct[k]
    elif (k in dct and merge_dct[k] is None
          and (isinstance(dct[k], dict) or isinstance(dct[k], list))):
      # Do not overwrite dicts and lists with empty entry.
      pass
    else:
      dct[k] = merge_dct[k]

def is_valid_file(arg):
  """
  Argparse 'type' callback.
  Validate that the argument is an URL or the path to an existing file.
  """
  if arg.startswith('http://') or arg.startswith('https://'):
    return { 'type': 'url', 'target': arg }

  if os.path.isfile(arg):
    return { 'type': 'file', 'target': os.path.abspath(arg) }

  raise argparse.ArgumentTypeError("File not found: {0}".format(arg))

def render_template(template, template_data, force_list=None, debug=False):

  if template['type'] == 'url':
    try:
      f = requests.get(template['target'])
      f.raise_for_status()
    except requests.exceptions.RequestException as e:
      print("Failed to download template: %s" % e)
      sys.exit(1)
    template = f.text
  else:
    with open(template['target'], 'r') as f:
      template = f.read()

  # Create the jinja2 environment.
  j2_env = Environment(loader=BaseLoader(),
                       extensions=['jinja2.ext.loopcontrols'],
                       trim_blocks=True, lstrip_blocks=True)

  # Dump the received data.
  if debug:
    print(json.dumps(template_data, indent=4), file=sys.stderr)

  # Render the template.
  # Loop until we get stable results.  The result we get from a template
  # rendering may still contain Jinja2 instructions.
  prev_result = template
  while True:
    result = j2_env.from_string(prev_result).render(template_data)
    if result == prev_result:
      break
    prev_result = result

  print(result)

if __name__ == '__main__':
  # Define arguments parser.
  parser = argparse.ArgumentParser(description='Helper to render a Jinja2 '
                                               'template using a JSON or XML '
                                               'file as data source.')
  parser.add_argument('TEMPLATE',
                      type=is_valid_file,
                      help='Path to the Jinja2 template file.')
  parser.add_argument('TEMPLATE_DATA',
                      type=is_valid_file,
                      nargs='+',
                      help='Path to JSON or XML file containing the data to be '
                           'filled in the template.')
  parser.add_argument('--force-list',
                      help='Comma-separated list of XML elements to be '
                           'considered as a list, even if there is only a '
                           'single child of a given level of hierarchy.')
  parser.add_argument('--debug',
                      action='store_true',
                      help='Log debugging information to stderr.')

  # Parse arguments.
  args=parser.parse_args()

  # Create list of XML elements that need to be considered as a list.
  force_list=None
  if args.force_list:
    force_list = args.force_list.split(',')

  # Open and load template source data file(s).
  data = {}
  for tmpl in args.TEMPLATE_DATA:
    if tmpl['type'] == 'url':
      try:
        f = requests.get(tmpl['target'])
        f.raise_for_status()
      except requests.exceptions.RequestException as e:
        print("Failed to download template data source: %s" % e)
        sys.exit(1)
      if f.headers['content-type'] == 'application/json':
          dict_merge(data, json.loads(f.text))
      elif f.headers['content-type'] == 'application/xml':
        dict_merge(data, xmltodict.parse(f.text, force_list=force_list))
    else:
      _, extension = os.path.splitext(tmpl['target'])
      with open(tmpl['target']) as data_file:
        if extension == '.xml':
          dict_merge(data, xmltodict.parse(data_file.read(), force_list=force_list))
        elif extension == '.json':
          dict_merge(data, json.load(data_file))

  # Render the template.
  render_template(args.TEMPLATE, data, force_list, args.debug)
