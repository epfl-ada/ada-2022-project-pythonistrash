from __future__ import annotations

import os

import math
import json
import nltk
import gzip
import pickle
import requests
import csv

import numpy as np
import pandas as pd
import seaborn as sns

import scipy.stats as stats
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
from collections import Counter
from functools import cmp_to_key

from nltk.sentiment import SentimentIntensityAnalyzer
import patsy.builtins as pat

import xml.etree.ElementTree as ET
import statsmodels.formula.api as smf

