"""Deterministic Markdown; simulated tables are labelled by construction."""

import json

DISCLAIMER = (
    "Simulation: shows model behaviour under the stated assumptions; "
    "it makes no claims about real users."
)
PAPER = (
    "https://www.asc.upenn.edu/sites/default/files/2021-03/"
    "Computing%20Krippendorff%27s%20Alpha-Reliability.pdf"
)


def percent(value):
    return "undefined" if value is None else f"{float(value) * 100:.2f}%"


def points(value):
    return "undefined" if value is None else f"{float(value) * 100:.2f} pp"


def cell(value):
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def table(lines, label, title, headers, rows):
    lines.extend(
        [
            "",
            f"## {label}: {title}",
            "",
            "| " + f"{label} " + " | ".join(headers) + " |",
            "|" + "---|" * len(headers),
        ]
    )
    lines.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in rows)


def report_markdown(result):
    simulated = result["label"] == "simulation"
    label = "Simulation" if simulated else "Real votes"
    lines = [
        DISCLAIMER if simulated else "Real votes: replay of supplied reviewer votes.",
        "",
        f"# {result['title']}",
    ]
    rows = []
    for method, stat in result["metrics"]["methods"].items():
        cost = stat["votes_per_decided_record"]
        rows.append(
            [
                method,
                f"{stat['correct']} / {stat['decided']} ({percent(stat['accuracy'])})",
                f"{stat['correct']} / {stat['all']} ({percent(stat['correct_all'])})",
                f"{stat['unresolved']} / {stat['all']} ({percent(stat['unresolved_rate'])})",
                "undefined" if cost is None else f"{cost:.2f}",
            ]
        )
    table(
        lines,
        label,
        "main comparison",
        [
            "method",
            "Correct / decided (accuracy)",
            "Correct / all",
            "Unresolved",
            "Counted votes / decided",
        ],
        rows,
    )
    alpha, ci = result["metrics"]["alpha"], result["metrics"]["accuracy_difference_ci"]
    alpha_text = (
        f"{alpha['value']:.6f}" if alpha["value"] is not None else f"undefined ({alpha['reason']})"
    )
    interval = (
        f"[{points(ci['lower'])}, {points(ci['upper'])}]"
        if ci["lower"] is not None
        else f"undefined ({ci['reason']})"
    )
    lines += [
        "",
        f"## {label}: agreement and paired comparison",
        "",
        f"Nominal Krippendorff alpha: **{alpha_text}**.",
        f"Pairable units: {alpha['pairable_units']}; values: {alpha['pairable_values']}.",
        "Agreement uses every supplied counted non-control vote, including votes unused "
        "after an early decision; abstentions are missing.",
        "",
        f"Accuracy difference (weighted − baseline): {points(ci['estimate'])}.",
        f"95% paired-record bootstrap CI: {interval}.",
        f"Resamples: {ci['resamples']}; seed: {ci['seed']}; "
        f"undefined draws: {ci['undefined_resamples']}.",
        "Each paired resample recomputes both correct/decided ratios. Reputation is not relearned.",
        "",
        f"## {label}: H1/H2 {'pipeline check' if result['synthetic'] else 'assessment'}",
        "",
        f"H1: {result['hypotheses']['H1']}",
        "",
        f"H2: {result['hypotheses']['H2']}",
    ]
    if result["synthetic"]:
        lines += [
            "",
            "Synthetic records: a pipeline check only, not a TIL-25 dataset result "
            "or evidence about real reviewers.",
        ]
    lines += [
        "",
        "## Assumptions",
        "",
        f"Control records: {len(result['control_record_ids'])}; excluded from both "
        "methods' accuracy and cost metrics.",
        "Records are processed whole, in the input CSV file order. Both methods receive "
        "the same ordered raw votes; each stops independently.",
        "Baseline: strict majority after each counted vote from 3 to 5; "
        "no reputation or control-task learning.",
    ]
    if simulated:
        lines += [
            "The simulated moderator resolves weighted escalations with the reference "
            "label for standard reputation updates; the automatic outcome remains "
            "unresolved for accuracy.",
            "Finite reviewer pools are sampled without replacement. Exhaustion fails "
            "explicitly; no conditioned redraw replaces abstentions.",
            "Control count rounds records × control share to the nearest integer, half up. "
            "Control votes receive only control updates, up to the counted-vote limit.",
        ]
        scenario = result["assumptions"]["scenario"]
        table(
            lines,
            label,
            "Assumptions — reviewer profiles",
            ["reviewer", "Assumed profile", "Assumed accuracy", "Assumed don't-know rate"],
            [
                [
                    r["id"],
                    r.get("profile", ""),
                    percent(r["accuracy"]),
                    percent(r["dont_know_rate"]),
                ]
                for r in scenario["reviewers"]
            ],
        )
        lines += [
            "",
            f"Seed: {result['seed']}; assumed control share: {scenario['control_share']}.",
        ]
    else:
        lines += [
            "No simulated reviewer accuracies are assumed. Escalations have no supplied "
            "moderator resolution in this format, so do not update standard reputation."
        ]
    table(
        lines,
        label,
        "control-task accuracy (weighted replay)",
        ["reviewer", "Correct / counted", "Accuracy", "Abstentions"],
        [
            [reviewer, f"{s['correct']} / {s['counted']}", percent(s["accuracy"]), s["abstained"]]
            for reviewer, s in result["metrics"]["control_accuracy"].items()
        ],
    )
    for field, methods in result["metrics"]["breakdowns"].items():
        rows = []
        for method, groups in methods.items():
            for group, stat in groups.items():
                rows.append(
                    [
                        group,
                        method,
                        f"{stat['correct']} / {stat['decided']}",
                        percent(stat["accuracy"]),
                        f"{stat['correct']} / {stat['all']} ({percent(stat['correct_all'])})",
                        stat["unresolved"],
                    ]
                )
        table(
            lines,
            label,
            f"accuracy by {field}",
            ["group", "Method", "Correct / decided", "Accuracy", "Correct / all", "Unresolved"],
            rows,
        )
    conditions = result["processing"]
    lines += [
        "",
        "## Processing and provenance",
        "",
        f"Scenario: {cell(result['scenario'])}; input label: {result['label']}.",
        f"Git commit: `{conditions['git_commit']}`.",
        f"Implementation SHA-256: `{conditions['implementation_sha256']}`.",
        f"Python: {conditions['python']}; Django: {conditions['django']}.",
        "Execution timestamps are omitted so identical inputs, implementation and commit "
        "produce byte-identical artifacts.",
        "",
        "Frozen quality settings:",
        "",
        "```json",
        json.dumps(result["settings"], indent=2, sort_keys=True),
        "```",
    ]
    table(
        lines,
        label,
        "input SHA-256",
        ["input", "SHA-256"],
        [
            [f"{name}: {source['path']}", f"`{source['sha256']}`"]
            for name, source in result["inputs"].items()
        ],
    )
    lines += [
        "",
        "## Limitations and validation",
        "",
        "The sample is small; reference labels can be wrong. The interval is exploratory, "
        "not proof of superiority. No settings were tuned to these outputs.",
        "The bootstrap describes fixed replay outcomes; it does not model learning "
        "uncertainty, reviewer dependence, or new reviewer populations.",
        "Alpha is tested against an exact hand-calculated fraction and "
        f"[Krippendorff's published missing-data example]({PAPER}), "
        "section C, pp. 4–5 (printed 0.743).",
    ]
    return "\n".join(lines) + "\n"
