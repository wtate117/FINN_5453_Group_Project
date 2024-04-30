#%% Import Functions
import pandas as pd
import pandas_datareader.data as pdr
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import scipy.optimize as sco
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yfinance as yf
from matplotlib.figure import Figure
import statsmodels.api as sm
import plotly.graph_objects as go
import requests
import seaborn as sns
from datetime import datetime, timedelta, date
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from dateutil.relativedelta import relativedelta