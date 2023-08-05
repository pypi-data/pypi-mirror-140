#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import click

from .init import init_project


@click.group()
def project_group() -> None:
    """Manage machine learning projects.

    Commands:
        |  init-project

    """
    pass


project_group.add_command(init_project, "init")
