from __future__ import print_function
import httplib2
import os
import random

from apiclient import discovery,errors
from oauth2client import client,tools
from oauth2client.file import Storage
from email.mime.text import MIMEText
from copy import deepcopy
import base64


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Your Application Name'

#Your email address.
MYMAIL = "change@me.com"
#Insert all the Names of Secret Santa participants here
GiverList = ["Insert","Participants","Here"]
ReceiverList = deepcopy(GiverList)
#Inserst their Email adresses here
EmailDic = {
"Insert" : "mail@addresses.com",
"Participants": "mail@addresses.com",
"Here": "mail@addresses.com"
}


def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print ('Message Id: %s' % message['id'])
    return message
  except errors.HttpError, error:
    print ('An error occurred: %s' % error)

def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string())}

def mailRetrieval(mail):
    """Retrieves the sent Mail and creates a Message Object.
    Args:
        mail: Email Address of Receiver
    """
    with open("messageTo"+mail+".txt","r") as f:
        message = {'raw': f.read()}
        f.close()
    return message

def changeReceiver(mail,newmail):
    """Changes the Receiver Email

    Args:
        mail: mail Adress of Receiver
        newmail: mail Adress which it should be changed to
    """
    message = mailRetrieval(mail)
    body = base64.decodestring(message['raw'])
    body = body.replace(mail,newmail,1)
    return {'raw': base64.urlsafe_b64encode(body)}

def sendSecretSantaMail(service):
    """Given a List of People and a Dictionary of email adresses corrosponding
    to the people, this programm sends all the people their Secret Santa Partner
    via google Mail
    """
    SecretSantaDic = {}
    for value in GiverList:
        rand = random.randint(0, len(ReceiverList) -1)
        while value == ReceiverList[rand]:
            rand = random.randint(0, len(ReceiverList) -1)
        SecretSantaDic[value] = ReceiverList[rand]
        ReceiverList.remove(ReceiverList[rand])
    for key, value in SecretSantaDic.iteritems():
        message = create_message(MYMAIL,EmailDic[key],"You are the Secret Santa for",value)
        with open("messageTo"+EmailDic[key]+".txt","wb") as f:
            f.write(message["raw"])
            f.close()
        send_message(service,"me",message)

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():

    #This is the gmail Authorization, you may need to run the programm twice,
    #if you aren't authorized yet.
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    #Some Validation of user Input:
    if(len(GiverList) != len(EmailDic) or set(EmailDic.iterkeys()) != set(GiverList)):
        print("You forgot to give everyone an email address")
        return
    else:
        sendSecretSantaMail(service)
        print("All Mail send")


if __name__ == '__main__':
    main()
