"""Admin route for monitoring adaptive assigners.

This route tells the admin:

1. The current assignment weights
2. The probability that each condition is best
3. The cumulative proportion of users assigned to each condition so far
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from hemlock import Page
from hemlock.admin_route_utils import (
    bp,
    db,
    in_gitpod_ide,
    login_required,
    navbar,
    static_pages,
)
from hemlock.questions import Label
from hemlock.utils.statics import pandas_to_html, recompile_at_interval

from .assign import assigners

navbar[1].insert(1, ("Ax", "/admin-ax"))


@bp.route("/admin-ax")
@login_required
def admin_ax() -> str:
    """Admin route.

    Returns:
        str: HTML.
    """
    if in_gitpod_ide():
        # socket has difficulty connecting the Gitpod IDE
        page = Page(label := Label(), navbar=navbar, forward=False, back=False)
        get_weights(label)
        return page.render()

    ax_page_key = "ax"
    if ax_page_key not in static_pages:
        page = Page(
            recompile_at_interval(30000, label := Label(compile=get_weights)),
            navbar=navbar,
            forward=False,
            back=False,
        )
        get_weights(label)
        db.session.add(label)
        db.session.commit()
        static_pages[ax_page_key] = page.render()

    return static_pages[ax_page_key]


def get_weights(ax_label: Label) -> None:
    """Get the assigner's summary statistics.

    Args:
        ax_label (Label): Label on which to print out summary stats.
    """
    tables = []
    for assigner in assigners:
        assigner.refresh()
        if len(assigner.factor_names) == 1:
            index = [value[0] for value in assigner.possible_assignments]
        else:
            index = pd.MultiIndex.from_tuples(
                assigner.possible_assignments, names=assigner.factor_names
            )

        # use uniform weights if the assigner doesn't have weights yet
        uniform = np.full(len(index), 1 / len(index))
        df = pd.DataFrame(
            {
                "Weights": assigner.weights or uniform,
                "Pr. Best": assigner.pr_best or uniform,
            },
            index=index,
        )
        cum_assigned = assigner.get_cum_assigned()
        if (cum_assigned["count"] > 0).any():
            cum_assigned["Proportion"] = (
                cum_assigned["count"] / cum_assigned["count"].sum()
            )
        df = df.join(cum_assigned.rename(columns={"count": "Cum. Assigned"}))

        tables.append(pandas_to_html(df, float_format=lambda x: f"{x:.3f}"))

    ax_label.label = "".join(tables)
