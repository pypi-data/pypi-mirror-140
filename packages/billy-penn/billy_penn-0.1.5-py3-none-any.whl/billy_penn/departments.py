import json

# from functools import lru_cache
from typing import Optional

import numpy as np
import pandas as pd

# import warnings
from pydantic import BaseModel

from . import DATA_DIR

# from fuzzywuzzy import fuzz, process


class Department(BaseModel):
    """
    An object representing a City of Philadelphia department.

    Parameters
    ----------
    name : str
        the name of the department
    dept_code : str
        the number of the department
    abbreviation : str, optional
        The department abbreviation
    """

    name: str
    dept_code: str
    abbreviation: Optional[str] = None

    def __repr__(self):
        return f"<Department: {self.name}>"

    def __str__(self):
        return self.name


def load_city_departments(include_line_items=False, include_aliases=False):
    """Load City departments."""

    depts = []
    with (DATA_DIR / "depts.json").open("r") as ff:
        data = json.load(ff)
    for d in data:

        # Pop the line items
        line_items = d.pop("line-items") if "line-items" in d else None

        # Add the main department
        depts.append(Department(**d))

        # Add the line items
        if include_line_items and line_items is not None:
            for line_item in line_items:
                depts.append(Department(**line_item))

    # Create the datafrmae
    out = (
        pd.DataFrame([dict(dept) for dept in depts])
        .replace(to_replace=[None], value=np.nan)
        .drop_duplicates(subset=["dept_code"])
    )

    assert out["dept_code"].duplicated().sum() == 0

    # Add aliases
    if include_aliases:

        # Get alias lookup
        lookup = pd.read_excel(DATA_DIR / "dept_names_lookup.xlsx", dtype=str)[
            ["dept_name", "dept_code"]
        ].drop_duplicates()

        aliases_column = []
        for _, row in out.iterrows():

            # Get lookup match
            matches = lookup.query(f"dept_code == '{row['dept_code']}'")
            aliases = []
            if len(matches):
                aliases = matches["dept_name"].tolist()
                if row["name"] not in aliases:
                    aliases.append(row["name"])
                if row["abbreviation"] not in aliases:
                    aliases.append(row["abbreviation"])

            aliases_column.append(aliases)

        out["aliases"] = aliases_column
        out = (
            out.join(out["aliases"].explode().rename("alias"))
            .drop(columns=["aliases"])
            .reset_index(drop=True)
            .assign(alias=lambda df: df["alias"].fillna(df["name"]))
            .drop_duplicates()
        )

    return out.rename(columns={"name": "dept_name"})


# @lru_cache(maxsize=None)
# def lookup(val, field=None, match_threshold=95):
#     """
#     Perform a lookup operation on the input value to return a matching City of
#     Philadelphia department. The match will be fuzzy if no exact matches are
#     identified first.

#     If ``field`` is provided, only match against the specified department attribute.

#     Notes
#     -----
#     -   If ``val`` is an integer, the lookup operation will try to match by
#         department number only
#     -   This will match against both ``Department`` and ``SubDepartment`` objects

#     Parameters
#     ----------
#     val : str, int
#         the value to use to identify a department

#     Returns
#     -------
#     Department, SubDepartment :
#         the matching department object
#     """
#     # check department number
#     if isinstance(val, int):
#         for dept in DEPARTMENTS:
#             if val == dept.number:
#                 return dept
#         raise ValueError(
#             "Input interpreted as a department number, but number is not valid"
#         )

#     def find_exact_matches(val, data):
#         for key in ["name", "abbr", "alias"]:
#             attrs = [getattr(d, key, None) for d in data]
#             match = attrs.index(val) if val in attrs else None
#             if match:
#                 return key

#     # search for exact matches
#     if field is None:
#         field = find_exact_matches(val, DEPARTMENTS)
#         if field is None:
#             field = find_exact_matches(val, SUBDEPARTMENTS)

#     # if no match yet, we'll do a fuzzy match
#     if field is None:
#         field = "fuzzy"

#     # try fuzzy matching
#     if field == "fuzzy":

#         # search for best score
#         best_score = 0
#         best_match = None
#         for key in ["name", "abbr", "alias"]:
#             match = process.extractBests(
#                 val,
#                 [getattr(d, key, None) for d in ALL],
#                 limit=1,
#                 scorer=fuzz.token_set_ratio,
#                 score_cutoff=match_threshold,
#             )
#             if len(match):
#                 match = match[0]

#             if len(match) and match[1] > best_score:
#                 best_score = match[1]
#                 field = key
#                 best_match = match[0]
#         val = best_match

#         # warn about low scores
#         if best_match is not None and best_score < 50:
#             warnings.warn(
#                 f"Trouble finding a good match: best matching score was {best_score}/100"
#             )

#     if val is None:
#         return None

#     # return
#     for dept in ALL:
#         if val == getattr(dept, field, None):
#             return dept

#     # if we get here, we didn't find a match
#     return None
