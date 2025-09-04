from flask import Blueprint, render_template, request, redirect, url_for
from models import House

list = Blueprint('search', __name__)
