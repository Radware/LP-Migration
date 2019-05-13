from flask import Flask, render_template
from app import app

@app.route('/', methods=['GET', 'POST'])
def main_index():
    return render_template('main.html')
