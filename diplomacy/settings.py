# ==============================================================================
# Copyright (C) 2019 - Philip Paquette
#
#  This program is free software: you can redistribute it and/or modify it under
#  the terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
#  details.
#
#  You should have received a copy of the GNU Affero General Public License along
#  with this program.  If not, see <https://www.gnu.org/licenses/>.
# ==============================================================================
""" Settings
    - Provides fixed diplomacy settings shared across project
"""
import os

DIPLOMACY_ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
PACKAGE_DIR = DIPLOMACY_ROOT_DIR
TIME_ZONE = 'America/Montreal'
PERMISSIVE_CLIENT_ORIGIN = True
if "PRESSGLOSS_URL" in os.environ:
    PRESSGLOSS_URL = os.environ['PRESSGLOSS_URL']
else:
    PRESSGLOSS_URL = 'http://129.114.99.77:5000'
