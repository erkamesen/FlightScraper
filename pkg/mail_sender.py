import smtplib
import logging

logging.basicConfig(filename='../errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(pathname)s - Line %(lineno)d - %(message)s')


class MailSender:

    def __init__(self, sender_mail, token, use,
                 mail_server="smtp.gmail.com", port=587):

        self._sender_mail = sender_mail
        self._token = token
        self._use = use
        self._mail_server = mail_server
        self._port = port

    def send_message(self, message, receiver):
        if not self._use:
            ...
        else:
            try:
                with smtplib.SMTP(self._mail_server, self._port) as connection:
                    connection.starttls()
                    connection.login(self._sender_mail, password=self._token)
                    connection.sendmail(from_addr=self._sender_mail,
                                        to_addrs=receiver,
                                        msg=message)

            except smtplib.SMTPAuthenticationError as e:
                logging.error(f"Warning - SMTPAuthenticationError: {e}")
                print("Check your Email or SMTP TOKEN !.!.!")

            except smtplib.SMTPRecipientsRefused as e:
                logging.error(f"Warning - SMTPRecipientsRefused: {e}")
                print(f"Recevier mail is invalid !! {e}")
