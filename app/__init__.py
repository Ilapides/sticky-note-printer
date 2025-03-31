from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

from app import routes