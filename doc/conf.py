from sphinx_mdolab_theme.config import *

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath("../"))

# -- Project information -----------------------------------------------------

project = "pyXDSM"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions.extend([
    "numpydoc",
    "sphinxcontrib.autodoc_pydantic",
])
numpydoc_show_class_members = False

# -- autodoc_pydantic configuration -------------------------------------------

# Show all configuration options for Pydantic models
autodoc_pydantic_model_show_json = True
autodoc_pydantic_model_show_config_summary = True
autodoc_pydantic_model_show_config_member = True
autodoc_pydantic_model_show_validator_members = True
autodoc_pydantic_model_show_field_summary = True
autodoc_pydantic_model_members = True
autodoc_pydantic_model_undoc_members = True

# Settings for fields
autodoc_pydantic_field_list_validators = True
autodoc_pydantic_field_doc_policy = "both"  # Show both docstring and description
autodoc_pydantic_field_show_constraints = True
autodoc_pydantic_field_show_alias = True
autodoc_pydantic_field_show_default = True

# Validator settings
autodoc_pydantic_validator_replace_signature = True
autodoc_pydantic_validator_list_fields = True

# mock import for autodoc
autodoc_mock_imports = ["numpy", "pydantic"]
