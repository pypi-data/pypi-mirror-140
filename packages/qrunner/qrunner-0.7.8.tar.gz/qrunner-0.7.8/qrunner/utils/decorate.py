# @Time    : 2022/3/3 16:38
# @Author  : kang.yang@qizhidao.com
# @File    : decorate.py
import pytest
import allure


def project(text):
    return allure.feature(text)


def module(text):
    return allure.story(text)


def title(text):
    return allure.title(text)


def data(*args, **kwargs):
    return pytest.mark.parametrize(*args, **kwargs)


