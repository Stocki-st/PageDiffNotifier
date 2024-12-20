from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import quote, unquote
from page_diff_notifier import PageDiffNotifier  
app = Flask(__name__)

# Initialize your notifier (make sure to replace with your actual initialization)
watcher = PageDiffNotifier()

@app.template_filter('url_encode')
def url_encode(s):
    return quote(s)

@app.route('/')
def index():
    watchlist = watcher.get_watchlist()  # Assuming you have a method to get the watchlist
    return render_template('index.html', watchlist=watchlist)

@app.route('/add', methods=['POST'])
def add_website():
    url = request.form['url']
    watcher.add_watcher(url)  # Assuming you have a method to add a website
    return redirect(url_for('index'))

@app.route('/remove/<path:url>', methods=['POST'])
def remove_website(url):
    url = unquote(url)
    watcher.remove_watcher(url)  # Assuming you have a method to remove a website
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)