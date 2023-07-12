from app.views import app
import threading
from app.views import delete_files

if __name__ == '__main__':
    timer = threading.Timer(60.0, delete_files)
    timer.start()





    app.run(debug=True,host='0.0.0.0',port=4000)
