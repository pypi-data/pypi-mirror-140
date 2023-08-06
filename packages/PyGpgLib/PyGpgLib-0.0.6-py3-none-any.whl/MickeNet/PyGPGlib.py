import os
import gnupg


class PyGpgLib:
    def __init__(self, gpghome, binary):
        self.gpghome = gpghome
        self.binary = binary

    def verify_content(self, path, passphrase, output_dir, output_ext='xml'):
        """

        :param path: The filepath to the file that is decrypted.
        :param passphrase:
        :param output_dir: The filepath where there file will be saved.
        :param output_ext: The extetion to use eg. xml or pgp xml default.
        :return: Path to the file with the decrypted content.
        """
        try:
            gpg = gnupg.GPG(gpgbinary=self.binary, gnupghome=self.gpghome, use_agent=True)
            name = os.path.splitext(os.path.basename(path))[0]
            new_path = os.path.join(os.path.dirname(output_dir), name + '.' + output_ext)

            with open(path, "rb") as content:
                content = content.read().decode('utf8')
                print(content)
                status = gpg.decrypt(content, output=new_path)
            print(status.status + " " + status.stderr)
            return new_path
        except Exception as e:
            raise Exception("GPG not working: "+str(e))

    def sign_content(self, path, passphrase, output_dir, output_ext='sig'):
        """ Sign the content at specified path using provided keyring
        :param path:        path of the content file
        :param passphrase:  key passphrase
        :param output_dir:  directory in which to write the signed file
        :param output_ext:  extension of the signed file
        """
        try:
            name = os.path.splitext(os.path.basename(path))[0]
            gpg = gnupg.GPG(gpgbinary=self.binary, gnupghome=self.gpghome)
            print(gpg.list_keys(True))
            gpg.encoding = 'utf-8'
            new_path = os.path.join(output_dir, name + '.' + output_ext)
            contents = open(path, 'rb')
            signed = gpg.sign_file( contents, passphrase=passphrase, clearsign=True)
            contents.close()
            with open(new_path, 'w') as output:
                output.write(str(signed))
            return new_path
        except Exception as e:
            raise Exception("GPG not working: "+str(e))

