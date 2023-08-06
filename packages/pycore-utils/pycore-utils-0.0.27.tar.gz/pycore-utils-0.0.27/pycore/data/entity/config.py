# coding=utf-8
import configparser


def init(path):
    global cf
    cf = configparser.RawConfigParser()
    cf.read(path)


def get(c, s):
    return cf.get(c, s)
