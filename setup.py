'''To start the server'''

from conferenceapp import app

if __name__ == '__main__':
    app.run(debug=True,port=8085)