#!/usr/bin/python

import os
import argparse
import json
import collections
import xmltodict
from jinja2 import Environment, FileSystemLoader

def dict_merge(dct, merge_dct):
  """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
  updating only top-level keys, dict_merge recurses down into dicts nested
  to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
  ``dct``.
  :param dct: dict onto which the merge is executed
  :param merge_dct: dct merged into dct
  :return: None
  """
  for k, v in merge_dct.iteritems():
    if (k in dct and isinstance(dct[k], dict)
          and isinstance(merge_dct[k], collections.Mapping)):
      dict_merge(dct[k], merge_dct[k])
    elif (k in dct and isinstance(dct[k], list)
          and isinstance(merge_dct[k], list)):
      dct[k] = dct[k] + merge_dct[k]
    else:
      dct[k] = merge_dct[k]

def is_valid_file(arg):
  """
  'Type' for argparse - checks that file exists.
  """
  if not os.path.isfile(arg):
    raise argparse.ArgumentTypeError("File not found: {0}".format(arg))
  return arg

def render_template(template, template_data, force_list=None):

  # Create the jinja2 environment.
  j2_env = Environment(loader=FileSystemLoader('/'),
                       trim_blocks=True, lstrip_blocks=True)

  # Dump the received data.
  # print(json.dumps(template_data, indent=4))

  # Render the template.
  result = j2_env.get_template(template).render(template_data).encode('utf-8')
  prev_result = ''

  # Loop until we get stable results.  The result we get from a template
  # rendering may still contain Jinja2 instructions.
  while result != prev_result:
    prev_result = result
    result = Environment().from_string(prev_result).render(template_data).encode('utf-8')

  print result

if __name__ == '__main__':
  # Handle arguments.
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
  args=parser.parse_args()

  force_list=None
  if args.force_list:
    force_list = args.force_list.split(',')

  # Open and load the JSON template(s) data file.
  data = {}
  for tmpl in args.TEMPLATE_DATA:
    _, extension = os.path.splitext(tmpl)
    with open(tmpl) as data_file:
      if extension == '.xml':
        dict_merge(data, xmltodict.parse(data_file.read(), force_list=force_list))
      elif extension == '.json':
        dict_merge(data, json.load(data_file))

  # Render the template.
  render_template(os.path.abspath(args.TEMPLATE), data, force_list)
