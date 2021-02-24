import pytest
import os
from bs4 import BeautifulSoup
from ..bxsoup import BxSoup
from ..object_models import (
    BxCollection,
    BxPath,
    BxInstruction
)

with open(os.path.join(os.path.dirname(__file__),
    'test_static/sample-fin-statement.html'
    ),'r') as f:
    HTML_TO_TEST = f.read()


def test_load_url():
    url = 'https://google.com'
    b = BxSoup(url)
    assert isinstance(b,BeautifulSoup)


def test_load_filepath():
    path = os.path.join(
        os.path.dirname(__file__),
        'test_static/sample-fin-statement.html'
    )
    b = BxSoup(path)
    assert isinstance(b,BeautifulSoup)


def test_load_html_str():
    html = HTML_TO_TEST
    b = BxSoup(html)
    assert isinstance(b,BeautifulSoup)

# other main methods

def test_generate_bxpaths():
    # arrange
    b = BxSoup(HTML_TO_TEST)
    expected_bxpath_cashAssets = BxPath(instructions=[
        BxInstruction(
            useIndex=False,
            useName=True, 
            tagName='html', 
            index=None, 
            attrs={'xmlns': 'http://www.w3.org/1999/xhtml'}
        ), 
        BxInstruction(
            useIndex=False,
            useName=True, 
            tagName='body', 
            index=None, 
            attrs={}
        ), 
        BxInstruction(
            useIndex=True, 
            tagName='div', 
            index=2, 
            attrs={'id': 'page-container'}
        ), 
        BxInstruction(
            useIndex=True, 
            tagName='div', 
            index=45, 
            attrs={
                'id': 'pf3', 
                'class': ['pf', 'w0', 'h0'], 
                'data-page-no': '3'
            }
        ), 
        BxInstruction(
            useIndex=True, 
            tagName='div', 
            index=0, 
            attrs={
                'class': ['pc', 'pc3', 'w0', 'h0']
            }
        ), 
        BxInstruction(
            useIndex=True, 
            tagName='div', 
            index=34, 
            attrs={
                'class': [
                    't', 
                    'm0', 
                    'x11', 
                    'h5', 
                    'y27', 
                    'ff2', 
                    'fs1', 
                    'fc0', 
                    'sc0', 
                    'ls1', 
                    'ws0'
                ]
            }
        )
    ], dataType='float')

    # act
    p_gen = b.generate_bxpaths('cashAssets')

    # result
    paths = [p for p in p_gen]
    assert len(paths)==1,f'Number of returns paths !=1. Got {len(paths)}'

    assert paths[0]==expected_bxpath_cashAssets,'Not return expected path'

def test_compile_bxpath():
    # arrange
    input_bxpath_cash_assets = BxPath(instructions=[
        BxInstruction(
            useIndex=False,
            useName=True,
            tagName='html', 
            index=None, 
            attrs={'xmlns': 'http://www.w3.org/1999/xhtml'}
        ), 
        BxInstruction(
            useIndex=False,
            useName=True,
            tagName='body', 
            index=None, 
            attrs={}
        ), 
        BxInstruction(
            useIndex=True, 
            tagName='div', 
            index=2, 
            attrs={'id': 'page-container'}
        ), 
        BxInstruction(
            useIndex=True, 
            tagName='div', 
            index=45, 
            attrs={
                'id': 'pf3', 
                'class': ['pf', 'w0', 'h0'], 
                'data-page-no': '3'
            }
        ), 
        BxInstruction(
            useIndex=True, 
            tagName='div', 
            index=0, 
            attrs={
                'class': ['pc', 'pc3', 'w0', 'h0']
            }
        ), 
        BxInstruction(
            useIndex=True, 
            tagName='div', 
            index=34, 
            attrs={
                'class': [
                    't', 
                    'm0', 
                    'x11', 
                    'h5', 
                    'y27', 
                    'ff2', 
                    'fs1', 
                    'fc0', 
                    'sc0', 
                    'ls1', 
                    'ws0'
                ]
            }
        )
    ], dataType='float')
    b = BxSoup(HTML_TO_TEST)

    # act
    result = b.compile_bxpath(input_bxpath_cash_assets)

    # result
    assert result == 225000.00


def test_clean_text_1():
    b = BxSoup(HTML_TO_TEST)
    test_s = '$î€ƒî€ƒî€ƒî€ƒî€ƒî€ƒî€ƒî€ƒî€ƒî€ƒ225,000'
    exp_s = '$                              225,000'

    assert b.clean_text(test_s)==exp_s