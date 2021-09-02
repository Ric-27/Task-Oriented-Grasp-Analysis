# included
import sys
import os
import random
import math
import time
import warnings


# download required
import argparse
import ast
from glob import iglob
import keyboard
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
from numpy.linalg import matrix_rank
from openpyxl import load_workbook
import pandas as pd
from scipy.optimize import linprog
from scipy.linalg import null_space
from stl import mesh  # the real name is numpy-stl

# config
np.set_printoptions(suppress=True)
warnings.filterwarnings('ignore')
