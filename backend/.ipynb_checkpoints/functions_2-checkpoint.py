import requests
import json
import pandas as pd
from datetime import datetime
import re
import ast
import operator
import streamlit as st
import time
import pandas as pd
import numpy as np
import os
import openai
import backend.functions_2 as back

# --- 1. Keyword intent ---
CONTACT_KEYWORDS = ["утас", "contact", "холбоо барих"]
LOCATION_KEYWORDS = ["байршил", "location"]

# --- 2. Safe math evaluator ---
ops = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def safe_eval(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return ops[type(node.op)](safe_eval(node.left), safe_eval(node.right))
    else:
        raise ValueError("Invalid expression")

def is_math_expression(s):
    return re.fullmatch(r"[0-9+\-*/().\s]+", s) is not None

def calculate(expr):
    tree = ast.parse(expr, mode='eval')
    return safe_eval(tree.body)

# --- 3. Date format шалгах ---
def is_date(s):
    return re.fullmatch(r"\d{4}-\d{2}-\d{2}", s) is not None

# --- 4. Монгол банк API (жишээ endpoint) ---
def get_exchange_rate(date):
    url = f"https://api.mongolbank.mn/api/exchange-rate?start={date}&end={date}"
    try:
        res = requests.get(url)
        data = res.json()
        return data
    except Exception:
        return "Ханшийн мэдээлэл авахад алдаа гарлаа"

# --- MAIN ROUTER ---
def handle_query(user_query: str):
    q = user_query.lower()

    # 1. Contact
    if any(k in q for k in CONTACT_KEYWORDS):
        return "Манай холбоо барих утасны дугаар: 99887766"

    # 2. Location
    if any(k in q for k in LOCATION_KEYWORDS):
        return "Манай байршил: Galaxy tower 7 давхар, 705 тоот"

    # 3. Math
    if is_math_expression(q):
        try:
            return f"Хариу: {calculate(q)}"
        except:
            return "Бодож чадсангүй"

    # 4. Date → API
    if is_date(q):
        return get_exchange_rate(q)

    # 5. Default
    return user_query
