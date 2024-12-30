from flask import Flask, render_template, request
from parser import run_fetch_jobs  
import threading


app = Flask(__name__)


@app.route('/')
def index():
    dynamic_title = "Это домашнее задание. Урок 22"
    return render_template('index.html', dynamic_title=dynamic_title)


@app.route('/contacts')
def contacts():
    return render_template('contacts.html', email="example@example.com", phone="+123456789")


@app.route('/form', methods=['GET', 'POST'])
def form_view():
    if request.method == 'POST':
        query = request.form['query']
             
        result = []
        thread = threading.Thread(target=lambda: result.append(run_fetch_jobs(query)))
        thread.start()
        thread.join() 
        
        return render_template('results.html', query=query, results=result[0])
    return render_template('form.html')


if __name__ == '__main__':
    app.run(debug=True)