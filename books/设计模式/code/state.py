# coding: utf-8
from __future__ import print_function


class State(object):
    """基础状态."""

    def scan(self):
        """拨号，调到下个电台"""
        self.pos += 1
        if self.pos == len(self.stations):
            self.pos = 0
        print(u"Scaning...station is %s %s" %
             (self.stations[self.pos], self.name))


class AmState(State):

    def __init__(self, radio):
        self.radio = radio
        self.stations = ['1250', '1380', '1510']
        self.pos = 0
        self.name = 'AM'

    def toggle_amfm(self):
        print(u"Switch to FM")
        self.radio.state =  self.radio.fmstate


class FmState(State):

    def __init__(self, radio):
        self.radio = radio
        self.stations = ["81.3", "89.1", "103.9"]
        self.pos = 0
        self.name = "FM"

    def toggle_amfm(self):
        print(u"Switching to AM")
        self.radio.state = self.radio.amstate


class Radio(object):
    """一个收音机.它具有调频功能和切换AM/FM开关"""

    def __init__(self):
        self.amstate = AmState(self)
        self.fmstate = FmState(self)
        self.state = self.amstate

    def toggle_amfm(self):
        self.state.toggle_amfm()

    def scan(self):
        self.state.scan()


if __name__ == '__main__':
    radio = Radio()
    actions = [radio.scan] * 2 + [radio.toggle_amfm] + [radio.scan] * 2
    actions *= 2

    for action in actions:
        action()
    