from flask import Flask, render_template, redirect
from app import app


@app.route('/', methods=['GET', 'POST'])
def main_index():
    return render_template('main.html')


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return redirect("https://www.radware.com/RadwareSite/MediaLibraries/Images/favicon.png", code=302)
