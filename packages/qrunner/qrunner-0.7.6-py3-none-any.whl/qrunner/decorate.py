# @Time    : 2022/2/22 10:37
# @Author  : kang.yang@qizhidao.com
# @File    : decorate.py
import allure
import pytest


def title(text):
    return allure.title(text)


def module(text):
    return allure.feature(text)


def data(*args, **kwargs):
    return pytest.mark.parametrize(*args, **kwargs)
