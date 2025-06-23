#!/usr/bin/env python3

from wsgiref.handlers import CGIHandler
from tcp_monitor import application

CGIHandler().run(application)
