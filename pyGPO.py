from ldap3 import Server, Connection, NTLM, MODIFY_REPLACE, MODIFY_DELETE, SUBTREE
from ldap3.core.exceptions import LDAPBindError
import argparse
import textwrap
import sys

class bcolors:
    """
    Define colors for status output
    """
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class pyGPO:
    """
    Class for the pyGPO program
    """

    def __init__(self, args):
        self.args = args

    def run(self):
        """
        Run function to initialize the main program
        """

        if not self.args.domaincontroller:
            print(f"{bcolors.FAIL}[!]{bcolors.ENDC} Need a valid domain controller IP to authenticate use -h for help")
            exit()

        # Check if domain is set
        if not self.args.domain:
            print(f"{bcolors.FAIL}[!]{bcolors.ENDC} Need a valid domain to authenticate use -h for help")
            exit()        

        # Try to initialize connection with domain controller
        conn = self.init_conn()
        
        # Check if user just wants to query the linked objects for a GPO
        if self.args.gpodn and not self.args.link and not self.args.unlink:
            # User wants to list linked objects for GPO
            self.listLinksForGPO(conn)

        # Check if user wants to link a GPO
        if self.args.gpodn and self.args.link:
            # User wants to link a GPO
            self.linkGPO(conn)
        
        # Check if user wants to unlink a GPO
        if self.args.gpodn and self.args.unlink:
            # User wants to link a GPO
            self.unlinkGPO(conn)

        # Close LDAP connection
        conn.unbind()

    def init_conn(self):
        """
        Tries to setup a connection with LDAP3
        """

        # Create an LDAP server
        port = 389
        server = Server(self.args.domaincontroller, port=port)

        # Concatenate domain and username
        username = f'{self.args.domain}\{self.args.username}'
        
        # Create an LDAP connection and authenticate using NTLM
        try:
            conn = Connection(server, 
                              user=username, 
                              password=self.args.password, 
                              authentication=NTLM, 
                              auto_bind=True)
        except LDAPBindError:
            print(f"{bcolors.FAIL}[!]{bcolors.ENDC} Could not connect to server, invalid credentials?")
            exit()

        if conn.result["result"] == 0:
            print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC} Authenticated successfully to {self.args.domaincontroller} ({self.args.domain})")

        # Authentication successfully
        return conn

    def getBaseDN(self):
        """
        Function to retrieve the Base DN from the given GPO DN.
        """

        # Get base DN from GPO arg
        if not self.args.gpodn:
            print(f"{bcolors.FAIL}[!]{bcolors.ENDC} To link/enumerate GPO please set a valid gpo_dn use -h for help")
            exit()
        components = self.args.gpodn.split(',')
        if len(components) >= 2:
            base_dn = ','.join(components[-2:]).strip()   

        return base_dn    

    def listLinksForGPO(self, conn):
        """
        Function that gets all the links for a GPO
        """
        
        # Check if user just wants to query the linked objects for a GPO
        # User wants to list linked objects for GPO. Use LDAP to query the links
        base_dn = self.getBaseDN()
        conn.search(search_base=base_dn, 
                    search_filter=f"(gPLink={self.args.gpodn})", 
                    search_scope=SUBTREE, time_limit=3)

        if conn.entries:
            print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC} Linked objects to the GPO: \n")
            for entry in conn.entries:
                print(entry.entry_dn)
            print("-------------------------------")
        else:
            print(f"{bcolors.OKGREEN}[!]{bcolors.ENDC} GPO has no linked objects")
        return

    def linkGPO(self, conn):
        """
        Function that tries to link a specified object with a specified GPO
        """
        # Define the attributes to link the GPO to the object
        attributes = {
            'gPLink': [(MODIFY_REPLACE, [self.args.gpodn])]
        }

        # Modify the object to link the GPO
        conn.modify(self.args.link, attributes)

        if conn.result["result"] == 0:
            print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC} Linked GPO to object successfully.")
        else:
            print(f"{bcolors.FAIL}[!]{bcolors.ENDC} Failed to link GPO to object. Error:", conn.result)

        # List new links for GPO
        listLinks = input("\nList links for GPO? [Y/n]: ")
        if listLinks == '' or listLinks == 'y' or listLinks == 'Y':
            self.listLinksForGPO(conn)
        return

    def unlinkGPO(self, conn):
        """
        Function that tries to unlink a specified object with a specified GPO
        """
        # Define the attributes to unlink the GPO from the object
        attributes = {
            'gPLink': [(MODIFY_DELETE, [self.args.gpodn])]
        }
        # Modify the object to unlink the GPO
        conn.modify(self.args.unlink, attributes)

        if conn.result["result"] == 0:
            print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC} Unlinked GPO from object successfully.")
        else:
            print(f"{bcolors.FAIL}[!]{bcolors.ENDC} Failed to unlink GPO from opbject. Error:", conn.result)

        # List new links for GPO
        listLinks = input("\nList links for GPO? [Y/n]: ")
        if listLinks == '' or listLinks == 'y' or listLinks == 'Y':
            self.listLinksForGPO(conn)  
        return      

if __name__ == '__main__':

    # Define a parser for arguments
    parser = argparse.ArgumentParser(
        description='Python script for managing GPO remotely',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""Examples:

Get linked objects from GPO  pyGPO.py -dc 10.1.10.1 -d powercorp.local -u john -p 'John123' -g 'gpo_dn'
Link GPO to object           pyGPO.py -dc 10.1.10.1 -d powercorp.local -u john -p 'John123' -g 'gpo_dn' -l 'target_dn'
Unlink GPO to object         pyGPO.py -dc 10.1.10.1 -d powercorp.local -u john -p 'John123' -g 'gpo_dn' -ul 'target_dn'
            """ ))

    # Define arguments for the parser
    parser.add_argument('-dc', '--domaincontroller', help='Domain controller IP')
    parser.add_argument('-u', '--username', help='Specify username')
    parser.add_argument('-p', '--password', help='Specify password or LM:NTLM hash')
    parser.add_argument('-d', '--domain', help='Specify the domain')
    parser.add_argument('-g', '--gpodn', help='Specify the target GPO dn')
    parser.add_argument('-l', '--link', help='Specify the target object to link')
    parser.add_argument('-ul', '--unlink', help='Specify the target object to unlink')
    args = parser.parse_args()

    # Intro
    intro = """
pyGPO.py by Incendium. Please use responsibly.
-------------------------------------------------------------------------
    """

    print(intro)

    # If there is less than 2 arguments, we will print out the help menu.
    if len(sys.argv[1:]) < 2:
        print("pyGPO.py [-h] [-u --user] [-p --password] [-d --domain] [-g --gpodn] [-l --link] [-ul --unlink] [-dc --domaincontroller]")
        print("")
        print(parser.epilog)
        sys.exit(0)

    # Parse arguments to pyGPO class.
    pygpo = pyGPO(args)

    # Call the run function in the pyGPO class.
    pygpo.run()

