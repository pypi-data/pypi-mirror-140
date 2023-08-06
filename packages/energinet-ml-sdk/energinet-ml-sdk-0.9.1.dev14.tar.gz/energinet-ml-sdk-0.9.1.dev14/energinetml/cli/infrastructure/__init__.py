#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import click

from .init import init_infrastructure


@click.group()
def infrastructure_group():
    """Manage cloud infrastructure for machine learning projects.

    Commands:
        |  init-infrastructure

    """
    pass


infrastructure_group.add_command(init_infrastructure, "init")
