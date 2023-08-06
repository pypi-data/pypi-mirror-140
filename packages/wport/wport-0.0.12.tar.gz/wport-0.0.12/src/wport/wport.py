"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mwport` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``wport.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``wport.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
from colorama import Fore
import re
import json
import textwrap

parser = argparse.ArgumentParser(description='Search for a port number or service name.')

# Set the argument
parser.add_argument('ARG', metavar='Port or Service', help='Default port number OR service name')

# Get the argument
args = parser.parse_args()
Arg = args.ARG

def main(args=None):
    # Error message if port doesn't exist
    ErrorNotFound = Fore.RED + "ERROR: port or service name not found." + Fore.WHITE

    # Read the dictionary file
    f = open('./AllPorts.json')
    data = json.load(f)ind_packages('src/wport')
    f.close()

    Allports = data['Allports']
    def PrintResult(rs):
      # Setup the data
      Title = 'WPORT : RESULTS'
      PortNo = Fore.YELLOW + rs['nb'] + Fore.WHITE
      Service = Fore.RED + rs['name'] + Fore.WHITE
      Description = rs['desc']
      Link = Fore.GREEN + rs['link'] + Fore.WHITE
      TopBottom = '-'
      TitlePort = Fore.YELLOW + "PORT" + Fore.WHITE
      TitleName = Fore.RED + "SERVICE NAME" + Fore.WHITE
      TitleLink = Fore.GREEN + "PENTESTING TIPS" + Fore.WHITE
      # Wrap this text.
      wrapper = textwrap.TextWrapper(width=108)
      WrappedDesc = wrapper.wrap(Description)

      # Show the result
      print("")
      print(TopBottom.center(110,'-'))
      print("|" + Title.center(108) + "|")
      print(TopBottom.center(110,'-'))
      print("|" + TitlePort.center(32) + "|" + TitleName.center(33) + "|" + TitleLink.center(71) + "|")
      print("|" + PortNo.center(32) + "|" + Service.center(33) + "|" + Link.center(71) + "|")
      print(TopBottom.center(110,'-'))
      # Print the wrapped description
      for element in WrappedDesc:
          print("|" + element.center(108) + "|")
      
      print(TopBottom.center(110,'-'))

    def PortNB(PN):
        PN = int(PN)
        if PN >= 6660 and PN <= 7000: # IRC
            SelectedPort = next((item for item in Allports if item['nb'] == '194, 6667, 6660-7000'), ErrorNotFound)
        elif PN >= 1522 and PN <= 1529: # Oracle TNS Listener
            SelectedPort = next((item for item in Allports if item['nb'] == '1521, 1522-1529'), ErrorNotFound)
        elif PN >= 49152 and PN <= 49160: # GlusterFS
            SelectedPort = next((item for item in Allports if item['nb'] == '124007, 24008, 24009, 49152+'), ErrorNotFound)
        else:
            PN = str(PN)
            SelectedPort = next((item for item in Allports if re.search(r'\b'+PN+r'\b', item['nb'])), ErrorNotFound)
        
        if SelectedPort != ErrorNotFound:
            PrintResult(SelectedPort)

        else:
            print(SelectedPort)

    def ServiceN(SN):
        #ServiceNames = [i for i, x in enumerate(Allports) if re.search(r'\b'+SN+r'\b', x['name'])]
        SelectedPort = next((item for item in Allports if re.search(r'(?i)\b'+SN+r'\b', item['name'])), ErrorNotFound)
            
        if SelectedPort != ErrorNotFound:
            PrintResult(SelectedPort)
            
        else:
            print(SelectedPort)

    if Arg.isnumeric():
        PortNB(Arg)
    elif not Arg.isnumeric():
        ServiceN(Arg)
    else:
        print(ErrorNotFound)
        exit()