"""Configuration constants for Personal Banking Customer Support Agent.

This file contains shared configuration that can be customized for different bank deployments.
"""

import os

# Bank configuration
# You can substitute any bank name, this agent looks up data with web search on the bank name.
BANK_NAME = os.getenv("BANK_NAME", "Wells Fargo")
BANK_LOCATION = "San Francisco, CA"
