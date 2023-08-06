import os
import sys
import argparse
import configparser
import requests
import toga
from toga.style.pack import COLUMN, ROW
import emoji
from .version import author, homepage, version

WIDTH = 400
HEIGHT = 200
PADDING = 10
WIDTH_LABELS = 100
WIDTH_CONTENT = WIDTH - (PADDING * 2)
WIDTH_BUTTON = (WIDTH_CONTENT - (PADDING*3)) / 4

DEFAULT_LOCATION = 'Working from home'
DEFAULT_STATUS = 'Online and available'
DEFAULT_EMOJI = ':green_circle:'

# runtime configuration
runtime = {'data':{}}

# ---------------------------------------------------------------------------
#                                                             error outputs
# ---------------------------------------------------------------------------

def fatal_cli(template, *args):
  print('Error', 'FATAL: ' + template % args)
  sys.exit(1)

def fatal_gui(sender):
  # TODO: replace with following when accepted:
  # https://github.com/beeware/toga/pull/1435
  #sender.main_window.error_dialog('Fatal!', f"Error on startup: {runtime['fatal']}")
  #sender.exit()
  sender.interface.main_window.error_dialog('Fatal!', f"Error on startup: {runtime['fatal']}")
  sender.interface.exit()

# ---------------------------------------------------------------------------
#                                                             API calls
# ---------------------------------------------------------------------------

def query():
  get_uri = f"{runtime['uri']}/users/{runtime['uuid']}"
  return requests.get(get_uri)

def update(data):
  headers = {'X-API-KEY': runtime['key']}
  patch_uri = f"{runtime['uri']}/users/{runtime['uuid']}"
  return requests.patch(patch_uri, headers=headers, data=data)

# ---------------------------------------------------------------------------
#                                                             GUI building
# ---------------------------------------------------------------------------

def build(app):

  def cancel_handler(widget):
    # pylint: disable=unused-argument
    app.exit()

  def check_handler(widget):
    # pylint: disable=unused-argument
    data = {
      'location': l_input.value,
      'status': emoji.emojize(s_input.value),
      'status_emoji': emoji.emojize(e_input.value)
    }
    # submit data using requests
    info.value = data

  def submit_handler(widget):
    # pylint: disable=unused-argument
    data = {
      'location': l_input.value,
      'status': emoji.emojize(s_input.value),
      'status_emoji': emoji.emojize(e_input.value)
    }
    info.value = data
    try:
      r = update(data)
    except requests.ConnectionError:
      app.main_window.error_dialog(
        'Error',
        'Could not connect to server for update'
      )
    else:
      info.value = r.text
      if r.status_code == 200:
        app.exit()
      else:
        app.main_window.error_dialog(
          'Error',
          'Update request failed with HTTP status {r.status_code}: "{r.text}"'
        )

  # set application window size
  window = app.main_window
  window.size = (WIDTH, HEIGHT)

  # set application placement
  # TODO: positioning not possible as of this writing
  #       See https://github.com/beeware/toga/pull/1395
  # also: https://github.com/beeware/toga/discussions/1433
  #window.position = (XPOS, YPOS)

  box = toga.Box()
  box.style.update(direction=COLUMN, padding=PADDING)

  # determine default values
  initial_location = runtime['data'].get('location', DEFAULT_LOCATION)
  initial_status = runtime['data'].get('status', DEFAULT_STATUS)
  initial_emoji = emoji.demojize(runtime['data'].get('status_emoji', DEFAULT_EMOJI))

  # location
  l_label = toga.Label('Location')
  l_input = toga.TextInput(initial=initial_location)
  l_box = toga.Box()
  l_box.style.update(direction=ROW, padding=PADDING)
  l_box.add(l_label)
  l_box.add(l_input)
  l_label.style.update(width=WIDTH_LABELS)
  l_input.style.update(flex=1)

  # status
  s_label = toga.Label('Status')
  s_input = toga.TextInput(initial=initial_status)
  s_box = toga.Box()
  s_box.style.update(direction=ROW, padding=PADDING)
  s_box.add(s_label)
  s_box.add(s_input)
  s_label.style.update(width=WIDTH_LABELS)
  s_input.style.update(flex=1)

  # status emoji
  e_label = toga.Label('Status emoji')
  #e_input = toga.Selection(items=['\N{grinning face with smiling eyes}'])
  e_input = toga.TextInput(initial=initial_emoji)
  e_box = toga.Box()
  e_box.style.update(direction=ROW, padding=PADDING)
  e_box.add(e_label)
  e_box.add(e_input)
  e_label.style.update(width=WIDTH_LABELS)
  e_input.style.update(flex=1)

  # submission info box
  info = toga.MultilineTextInput('', readonly=True)
  info.style.update(width=WIDTH_CONTENT, height=50, padding=PADDING, flex=1)

  # action buttons
  cancel = toga.Button('Cancel', on_press=cancel_handler)
  cancel.style.width = WIDTH_BUTTON

  check = toga.Button('Check', on_press=check_handler)
  check.style.width = WIDTH_BUTTON
  check.style.padding_left = PADDING * 2 + WIDTH_BUTTON

  submit = toga.Button('Submit', on_press=submit_handler)
  submit.style.width = WIDTH_BUTTON
  submit.style.padding_left = PADDING

  b_box = toga.Box()
  b_box.add(cancel)
  b_box.add(check)
  b_box.add(submit)
  b_box.style.update(direction=ROW, padding=PADDING)

  box.add(l_box)
  box.add(s_box)
  box.add(e_box)
  box.add(info)
  box.add(b_box)

  # check if the runtime configuration has errors
  if 'fatal' in runtime:
    # schedule display of fatal error dialog
    app.add_background_task(fatal_gui)

  return box

# ---------------------------------------------------------------------------
#                                                             configuration
# ---------------------------------------------------------------------------

def init():
  """
  Initialize application configuration and mode

  Raise exception if any issues

  Return list of fatal messages or None
  """

  # messages about conditions blocking startup
  fatal = []

  # determine default config file paths
  # Default paths are:
  # - XDG-standard local configuration directory
  # - old-school configuration location
  default_configs = [
    os.path.expanduser('~/.config/wai/wai.conf'),
    os.path.expanduser('~/.wai')
  ]

  # build argument parser
  parser = argparse.ArgumentParser(description='Query or update location and status information with Wai server.')
  subparsers = parser.add_subparsers(
    title='actions',
    dest='cmd',
    description='Perform actions non-interactively.  If unspecified, GUI will be launched',
  )

  # common arguments (regardless of command)
  parser.add_argument('-c', '--config', type=str,
                      help='configuration file',
                      default=default_configs)
  # unused but common so keeping just in case
  #parser.add_argument('-v', '--verbose',
  #                    help='debug output',
  #                    action='store_true')
  parser.add_argument('--uri', type=str,
                      help='URI for Wai server')
  parser.add_argument('--uuid', type=str,
                      help='user ID')

  # query command parser
  # pylint: disable=unused-variable  # not used but might need at some point
  parser_query = subparsers.add_parser('query',
                                       description='Query for current user info',
                                       help='query for current user info')
  parser_query.add_argument('--shell',
                            help='output results as shell variables',
                            action='store_true')

  # update command parser
  parser_update = subparsers.add_parser('update',
                                        description='Update user information',
                                        help='update user info')
  parser_update.add_argument('--key', type=str,
                             help="user's API key")
  parser_update.add_argument('--location', type=str,
                             help='set location')
  parser_update.add_argument('--status', type=str,
                             help='set status')

  # parse arguments
  args = parser.parse_args()

  # read in configuration
  config = configparser.ConfigParser(delimiters='=')
  res = config.read(args.config)
  if not res:
    fatal.append(f'Could not read configuration in {args.config}')
  else:
    # determine runtime config
    runtime['uri'] = args.uri or config['wai'].get('uri')
    if runtime['uri'] is None:
      fatal.append('Must provide URI for Wai server')
    runtime['uuid'] = args.uuid or config['wai'].get('uuid')
    if runtime['uuid'] is None:
      fatal.append('Must provide user ID')
    runtime['key'] = args.key if 'key' in args and args.key is not None else config['wai'].get('key')
    if args.cmd == 'update' and runtime['key'] is None:
      fatal.append('Must provide key if making updates')
    elif args.cmd == 'update' and not args.location and not args.status:
      fatal.append('Must provide at least one of location, status in update')

  return args if args.cmd else None, fatal or None

# ---------------------------------------------------------------------------
#                                                             main execution
# ---------------------------------------------------------------------------

def main():

  # determine runtime config
  args, errors = init()

  # CLI mode?
  if args:

    # if errors, just print errors
    if errors:
      fatal_cli('Errors in configuration: %s', '; '.join(errors))

    # carry out command as given
    if args.cmd == 'query':
      # retrieve current information
      try:
        r = query()
      except requests.ConnectionError:
        fatal_cli('Could not query server')
      if r.status_code == 200:
        data = r.json()
        if args.shell:
          print(f"STATUS=\"{data['status']}\"\nEMOJI=\"{data['status_emoji']}\"\nLOCATION=\"{data['location']}\"")
        else:
          print(data)
      else:
        fatal_cli('Could not query (%d): %s', r.status_code, r.json())
    elif args.cmd == 'update':
      try:
        r = update({
          'location': args.location,
          'status': args.status
        })
      except requests.ConnectionError:
        fatal_cli('Could not update server')
      if r.status_code == 200:
        print(f'Updated: {r.json()}')
      else:
        fatal_cli('Could not update (%d): "%s"', r.status_code, r.text)

    return None

  # GUI mode
  if errors:
    runtime['fatal'] = ';\n'.join(errors)
  else:
    # retrieve current information
    try:
      r = query()
    except requests.ConnectionError:
      runtime['fatal'] = 'Could not query server'
    else:
      if r.status_code == 200:
        runtime['data'] = r.json()
      else:
        runtime['fatal'] = r.json()

  return toga.App(
    'Wai Client',
    'net.p0nk.wai',
    author=author,
    description='Wai client app',
    version=version,
    home_page=homepage,
    startup=build
  )

def run():
  gui_app = main()
  if gui_app is not None:
    gui_app.main_loop()


if __name__ == '__main__':
  run()
