# KURS


1. Install Python (newest version)
2. Clone project into a folder
3. Install requirements by "pip install -r requirements.txt"
4. Navigate into the folder "web"
5. Migrate: python manage.py migrate
6. Run server by "python manage.py runserver"


# HTTPS Setup

To run your server in https, you need to do the following steps.

## Windows

1. install mkcert (refer https://github.com/FiloSottile/mkcert#windows)
2. Create your personal root certificate: mkcert -install
3. Navigate to your project folder eg. "/project" and run (replace XXX with your device IP): mkcert -cert-file cert.pem -key-file key.pem localhost 127.0.0.1 XXX.XXX.XXX.XXX
4. Copy cert.pem and key.pem to your folder with the manage.py 
5. Start your server with: python manage.py runserver_plus --cert-file cert.pem --key-file key.pem

If you want to access this webiste with an IOS device, you need to transfer the rootCert to this device. In this case, airdop the rootCA (mkcert -CAROOT for path) and follow this instructions:
https://github.com/FiloSottile/mkcert/issues/233#issuecomment-690110809

Now you can access your website on your iOS device with https.


Superuser:
admin
admin@admin.com
admin