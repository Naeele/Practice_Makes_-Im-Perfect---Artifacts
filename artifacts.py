# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "matplotlib==3.10.7",
#     "numpy==2.3.5",
#     "pandas==2.3.3",
#     "plotly==6.5.0",
#     "polars==1.35.2",
#     "pyarrow==22.0.0",
#     "regex==2025.11.3",
#     "kaleido==1.2.0"
# ]
# ///

import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # --- Here is the list of requirements for the following code to work properly ---

    import marimo as mo
    import polars as pl
    import numpy as np
    import regex as re
    import itertools
    from itertools import combinations
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    from matplotlib.patches import Patch
    import plotly.express as px
    from collections import Counter, defaultdict
    return (
        Counter,
        Patch,
        combinations,
        defaultdict,
        itertools,
        mo,
        np,
        pl,
        plt,
        px,
        re,
    )


@app.cell
def _(pl):
    # --- Read the csv file containing the list of Flawed, NA, Underspec. and Ok. for each paper of our corpus ---

    df_flaws = pl.read_csv("./form_flaws.csv")
    df_flaws
    return (df_flaws,)


@app.cell
def _(pl):
    # --- Read the csv file containing usefull information about the paper from our corpus ---

    df_data = pl.read_csv("./form_data.csv")
    df_data
    return (df_data,)


@app.cell
def _(df_data):
    # --- Here is a list of the columns in the form_data.csv file that correspond to the questions in our survey when investigating our corpus ---

    df_data.columns
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Reproduction of Figure 1: Number of Papers and Evaluated Artifacts per Conference per Year, with the Date Artifact Evaluations (AE) began.""")
    return


@app.cell
def _(df_data, itertools, np, pl, plt):
    # --- Deals with columns: "Year", "Conference", "Did the paper successfully participate in an artifact evaluation process?" ---

    # Years and conferences of interest
    years = list(range(2014, 2025))
    conferences = sorted(df_data["Conference"].unique().to_list())

    # Create a full grid of (Year, Conference) combinations = cartesian product between Year and Conference
    full_grid = pl.DataFrame(
        {"Year": [y for y, c in itertools.product(years, conferences)], 
         "Conference": [c for y, c in itertools.product(years, conferences)]}
    )

    # Compute total papers and evaluated papers per year + conference
    totals = (
        df_data.group_by(["Year", "Conference"])
        .agg(pl.len().alias("Total Papers"))
    )

    # Filter papers that only pass the evaluation process
    evaluated = (
        df_data.filter(pl.col("Did the paper successfully participate in an artifact evaluation process?") == "Yes")
        .group_by(["Year", "Conference"])
        .agg(pl.len().alias("Evaluated Papers"))
    )

    # Join the two aggregations
    summary = totals.join(evaluated, on=["Year", "Conference"], how="left").fill_null(0)

    # Increase global font size (optional)
    plt.rcParams.update({
        "font.size": 25,
        "axes.labelsize": 18,
        "axes.labelweight": "semibold",
        "xtick.labelsize": 18,
        "ytick.labelsize": 18,
        "xtick.minor.visible": False,
        "ytick.minor.visible": False,
        "ytick.major.width": 1.2,
        "xtick.major.width": 1.2,
        "font.weight": "bold",     # global bold
        "legend.fontsize": 18,
        # "legend.fontweight": "bold"
    })

    # ------------------------
    # --- Plotting section ---
    # ------------------------

    plt.figure(figsize=(15, 8))

    bar_width = 0.8 / len(conferences)  # to make groups of bars per year
    x = np.arange(len(years))

    # --- Colorblind-safe colors + pattern ---
    colors = list(plt.get_cmap("tab20").colors)  # list of RGB tuples
    colors.append("black")
    hatches = '\\\\'

    # --- Start Evaluation artifact year dictionary ---
    start_years = {
        "USENIX SECURITY SYMPOSIUM": 2020,
        "NDSS": 2024,
        "CCS": 2024,
        "S&P": None,
        "MICRO": 2021,
        "ISCA": 2023,
        "HPCA": 2022,
        "ASPLOS": 2020
    }

    for i, conf in enumerate(conferences):
        conf_data = summary.filter(pl.col("Conference") == conf)

        y_total = [conf_data.filter(pl.col("Year") == year)["Total Papers"].item(0) if year in conf_data["Year"].to_list() else 0 for year in years]
        y_total = [max(0.1, value) for value in y_total]

        y_eval  = [conf_data.filter(pl.col("Year") == year)["Evaluated Papers"].item(0) if year in conf_data["Year"].to_list() else 0 for year in years]

        # --- Base position for each conference within a given year ---
        pos = x + i * bar_width - (len(conferences) - 1) * bar_width / 2

        plt.bar(pos, y_total, width=bar_width,
                color=colors[i % len(colors)], label=f"{conf}",
                edgecolor='black', alpha=0.7)
        plt.bar(pos, y_eval, width=bar_width,
                color='none', edgecolor='black', hatch=hatches,
                label=f"Evaluated Artifact" if i == 0 else "")

        # --- Draw start-of-AE vertical line aligned with this conference’s bar ---
        start = start_years.get(conf.upper())
        if start is not None and start in years:
            year_idx = years.index(start)
            line_x = pos[year_idx]  # offset line to that conference’s bar position
            if conf == "USENIX Security Symposium":
                line_y = 7.25
            else:
                line_y = 7.25
            plt.axvline(line_x, color=colors[i % len(colors)], linestyle='--', linewidth=1)
            plt.text(line_x, line_y, f"{conf} starts AE",
                     rotation=90, fontsize=15.5, color=colors[i % len(colors)],
                     va='top', ha='right')

    plt.xticks(x, years)
    plt.xlabel("Year", fontsize=25)
    plt.ylabel("Number of Papers", fontsize=25)
    plt.title("Number of Papers and Evaluated Artifacts per Conference per Year")
    plt.legend(ncol=2, fontsize=14)
    plt.tight_layout()
    #plt.savefig("number_of_papers_and_evaluated_artifact.pdf")
    plt.show()
    return (start_years,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Reproduction of Figures 6, 16 and 17: The proportion of surveyed papers that make their code, material, and documentation available to reproduce their results, along with the date that Artifact Evaluation (AE) began, if applicable.
    For all conferences, architecture conferences only and security conferences only.
    """
    )
    return


@app.cell
def _(defaultdict, df_data, df_flaws, pl, plt, start_years):
    df_with_C3 = df_data.join(df_flaws, on="Title", how="left")
    df_with_C3.select(pl.col("Title"), pl.col("C3\nNo code / material / documentation to reproduce"))

    # --- Statuses of flaws ---
    statuses = ["Ok", "Flawed", "Underspec., Incomplete", "Underspec., Unclear, Incomplete"] #, "Underspec., Unclear"

    # --- Define custom colors per category ---
    color_map = {
        "Ok": "#2ca02c",                                       # green
        "Flawed": "#d62728",                                   # red
        "Underspec., Unclear, Incomplete": "#ff7f0e",          # orange
        "Underspec., Incomplete": "#ffbf00"                    # yellow
    }

    # --- Define conference groups ---
    sec_confs = ["NDSS", "USENIX Security Symposium", "S&P", "CCS"]
    archi_confs = ["ISCA", "HPCA", "MICRO", "ASPLOS"]

    def plot_group(df_subset, title):
        """Helper to make a proportion stacked area plot."""
        proportions = (
            df_subset.group_by("Year")
            .agg([
                *(pl.col("C3\nNo code / material / documentation to reproduce")
                    .eq(status)
                    .mean()
                    .alias(status)
                    for status in statuses)
            ])
            .sort("Year")
        )

        x = proportions["Year"].to_list()
        y = [proportions[s].to_list() for s in statuses]
        colors_ = [color_map[s] for s in statuses]

        # Legend renaming
        legend_labels = {
            "Ok": "Not Flawed",
            "Flawed": "Flawed",
            "Underspec., Incomplete": "Incomplete",
            "Underspec., Unclear, Incomplete": "Unclear & Incomplete"
        }

        plt.figure(figsize=(12, 6))
        plt.stackplot(x, y, labels=statuses, colors=colors_, alpha=0.85,
                      edgecolor="black", linewidth=0.3)

        # --- Add grouped AE start lines ---
        grouped = defaultdict(list)
        for conf, year in start_years.items():
            if year is not None:
                if conf in df_subset["Conference"].unique().to_list():
                    grouped[year].append(conf)
                elif conf == "USENIX SECURITY SYMPOSIUM" and \
                     "USENIX Security Symposium" in df_subset["Conference"].unique().to_list():
                    grouped[year].append("USENIX Security Symposium")

        for year, confs in grouped.items():
            plt.axvline(year, color="black", linestyle='--', linewidth=2.5)
            if year == 2024:
                plt.text(
                    year + 0.1, 0.97, f"{', '.join(confs)} start AE",
                    rotation=90, fontsize=13, color="black", weight="bold",
                    va='top', ha='left', transform=plt.gca().get_xaxis_transform()
                )
            elif year == 2020:
                plt.text(
                    year + 0.1, 0.97, f"{', '.join(confs)} start AE",
                    rotation=90, fontsize=11.5, color="black", weight="bold",
                    va='top', ha='left', transform=plt.gca().get_xaxis_transform()
                )
            else:
                plt.text(
                    year + 0.1, 0.97, f"{', '.join(confs)} starts AE",
                    rotation=90, fontsize=13, color="black", weight="bold",
                    va='top', ha='left', transform=plt.gca().get_xaxis_transform()
                )

        # ---- Y-axis in PERCENTAGE ----
        plt.gca().yaxis.set_major_formatter(lambda y, _: f"{int(y*100)}%")
        plt.yticks([0, 0.25, 0.5, 0.75, 1.0])

        # Labels
        plt.xlabel("Year", fontsize=25)
        plt.ylabel("Proportion of Papers", fontsize=25)

        # Ticks
        plt.xticks(list(range(2014, 2025)))

        # Legend WITHOUT title + renamed entries
        handles, labels = plt.gca().get_legend_handles_labels()
        new_labels = [legend_labels[l] for l in labels]
        plt.legend(handles, new_labels, loc="upper left", title=None)

        plt.ylim(0, 1)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.title(title)
        # plt.savefig(title + ".pdf")
        plt.show()

    # --- Plot code availability status proportion per year ---
    plot_group(df_with_C3,
               "Code Availability Status Distribution Per Year")
    return archi_confs, df_with_C3, plot_group, sec_confs


@app.cell
def _(archi_confs, df_with_C3, pl, plot_group):
    # --- Plot Architecture's papers only ---
    plot_group(df_with_C3.filter(pl.col("Conference").is_in(archi_confs)),
               "Code Availability Status Distribution Per Year – Architecture Conferences")
    return


@app.cell
def _(df_with_C3, pl, plot_group, sec_confs):
    # --- Plot Security papers's only ---
    plot_group(df_with_C3.filter(pl.col("Conference").is_in(sec_confs)),
               "Code Availability Status Distribution Per Year – Security Conferences")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Useful for following results: one dataframe line becomes one channel. 
    ## Covert channels alignment.
    """
    )
    return


@app.cell
def _(df_data, pl):
    # --- Split paper vs channel columns ---
    paper_cols = [
        "ID", "Title", "Year", "Conference",
        "Did the paper successfully participate in an artifact evaluation process?",
        "What benchmark do they provide?"
    ]

    # The repeated columns (1 set = 1 covert channel)
    channel_base_cols = [
        "How is it assessed?",
        "Error rate",
        "Comparison to other works",
        "How does it compare to other work?",
        "Is there any obvious threat to the comparison reliability?",
        "Number of configuration evaluated",
        "Is there a protocol (agreement/transmission)? ",
        "If so, what is it?",
        "Is there an error correction/management described?",
        "If so, what is used?",
        "Is the code available?",
        "Is there a minimal documentation (compilation, installation, usage)?"
    ]

    # We know we always have up to 3 sets of covert channels
    n_channels = 3

    # --- Split paper vs channel columns ---
    dfs = []

    for j in range(n_channels):
        suffix = "" if j == 0 else f"_duplicated_{j-1}"
        subset_cols = [c + suffix for c in channel_base_cols if c + suffix in df_data.columns]

        if not subset_cols:
            continue

        tmp = df_data.select(paper_cols + subset_cols)
        # Rename to base names
        rename_map = {c + suffix: c for c in channel_base_cols if c + suffix in df_data.columns}
        tmp = tmp.rename(rename_map)

        # Add index
        tmp = tmp.with_columns(pl.lit(j + 1).alias("covert_channel_index"))
        dfs.append(tmp)

    # --- Concatenate all the non-empty subsets ---
    long_df = pl.concat(dfs) if dfs else pl.DataFrame()

    # --- Determine which rows actually have covert channel info ---
    long_df = long_df.with_columns(
        has_channel = pl.col("How is it assessed?").is_not_null() & (pl.col("How is it assessed?") != "")
    )

    # --- Separate papers with at least one covert channel vs. none ---
    papers_with_channel = (
        long_df
        .filter(pl.col("has_channel"))
        .select("ID")
        .unique()
    )

    # --- All paper metadata (for possible empty ones) ---
    paper_df = df_data.select(paper_cols).unique(subset=["ID"])

    # --- Papers that have NO covert channel ---
    papers_without_channel = (
        paper_df.join(papers_with_channel, on="ID", how="anti")
        .with_columns([
            pl.lit(None).alias("How is it assessed?"),
            *[pl.lit(None).alias(c) for c in channel_base_cols if c != "How is it assessed?"],
            pl.lit(None).alias("covert_channel_index"),
            pl.lit(0).cast(pl.UInt32).alias("num_covert_channels_in_paper")  # type in UInt32 to avoid problem in the final contatenation
        ])
    )

    # --- Keep only rows with real covert channels ---
    long_df = long_df.filter(pl.col("has_channel")).drop("has_channel")

    # --- Count number of channels per paper ---
    count_df = long_df.group_by("ID").agg(pl.len().alias("num_covert_channels_in_paper"))

    # --- Merge that count ---
    long_df = long_df.join(count_df, on="ID", how="left")

    # --- Fill nulls (for papers with no channels) ---
    long_df = long_df.with_columns(
        pl.col("num_covert_channels_in_paper").fill_null(0).cast(pl.UInt32)
    )

    # --- Final merge: covert-channel papers + no-channel papers ---
    final_covert_df = pl.concat([long_df, papers_without_channel])

    final_covert_df
    return final_covert_df, paper_cols, paper_df


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Side channels alignment.""")
    return


@app.cell
def _(df_data, paper_cols, paper_df, pl, re):
    # --- Split paper vs channel columns ---
    # The repeated columns (1 set = 1 side channel)
    side_channel_base_cols = [
        "What are they attacking?",
        "Is the target version specified?",
        "How many samples are needed?",
        "Number of platform evaluated",
        "Comparison to other works",
        "How does it compare to other work?",
        "Is the code available?",
        "Is there a minimal documentation (compilation, installation, usage)?"
    ]

    # We know we always have up to 5 sets of side channels
    n_side_channels = 5

    # --- Split paper vs channel columns ---
    dfs_side = []

    for k in range(n_side_channels):
        if k == 0:
            subset_side_cols = [
                "What are they attacking?",
                "Is the target version specified?",
                "How many samples are needed?",
                "Number of platform evaluated_duplicated_0",
                "Comparison to other works_duplicated_2",
                "How does it compare to other work?_duplicated_2",
                "Is the code available?_duplicated_2",
                "Is there a minimal documentation (compilation, installation, usage)?_duplicated_2"
            ]
        else :
            subset_side_cols = [
                f"What are they attacking?_duplicated_{k-1}",
                f"Is the target version specified?_duplicated_{k-1}",
                f"How many samples are needed?_duplicated_{k-1}",
                f"Number of platform evaluated_duplicated_{k}",
                f"Comparison to other works_duplicated_{k+2}",
                f"How does it compare to other work?_duplicated_{k+2}",
                f"Is the code available?_duplicated_{k+2}",
                f"Is there a minimal documentation (compilation, installation, usage)?_duplicated_{k+2}"
            ]

        tmp_side = df_data.select(paper_cols + subset_side_cols)

        # Apply renaming
        rename_side_map = {}
        for c in subset_side_cols:
            # Remove any "_duplicated_X" part from the name
            base_name = re.sub(r"_duplicated_\d+$", "", c)
            rename_side_map[c] = base_name

        tmp_side = tmp_side.rename(rename_side_map)

        # Add index
        tmp_side = tmp_side.with_columns(pl.lit(k + 1).alias("side_channel_index"))
        dfs_side.append(tmp_side)

    # --- Concatenate all the non-empty subsets ---
    long_side_df = pl.concat(dfs_side) if dfs_side else pl.DataFrame()

    # --- Determine which rows actually have side channel info ---
    long_side_df = long_side_df.with_columns(
        has_channel = pl.col("What are they attacking?").is_not_null() & (pl.col("What are they attacking?") != "")
    )

    # --- Separate papers with at least one covert channel vs. none ---
    papers_with_side_channel = (
        long_side_df
        .filter(pl.col("has_channel"))
        .select("ID")
        .unique()
    )

    # --- Papers that have NO side channel ---
    papers_without_side_channel = (
        paper_df.join(papers_with_side_channel, on="ID", how="anti")
        .with_columns([
            pl.lit(None).alias("What are they attacking?"),
            *[pl.lit(None).alias(c) for c in side_channel_base_cols if c != "What are they attacking?"],
            pl.lit(None).alias("side_channel_index"),
            pl.lit(0).cast(pl.UInt32).alias("num_side_channels_in_paper")  # type in UInt32 to avoid problem in the final contatenation
        ])
    )

    # --- Keep only rows with real covert channels ---
    long_side_df = long_side_df.filter(pl.col("has_channel")).drop("has_channel")

    # --- Count number of channels per paper ---
    count_side_df = long_side_df.group_by("ID").agg(pl.len().alias("num_side_channels_in_paper"))

    # --- Merge that count ---
    long_side_df = long_side_df.join(count_side_df, on="ID", how="left")

    # --- Fill nulls (for papers with no channels) ---
    long_side_df = long_side_df.with_columns(
        pl.col("num_side_channels_in_paper").fill_null(0).cast(pl.UInt32)
    )

    # --- Final merge: side channel papers + no-channel papers ---
    final_side_df = pl.concat([long_side_df, papers_without_side_channel])

    final_side_df
    return (final_side_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## The total number of attacks in our corpus, including channel, side-channel, and covert-channel attacks.""")
    return


@app.cell
def _(df_data, final_covert_df, final_side_df, pl):
    # --- Add the total number of covert-channel attacks per paper ---
    covert_per_paper_count = (
        final_covert_df
        .group_by("ID")
        .agg(pl.max("num_covert_channels_in_paper").alias("num_covert_channels"))
    )

    # --- Add the total number of side-channel attacks per paper ---
    side_per_paper_count = (
        final_side_df
        .group_by("ID")
        .agg(pl.max("num_side_channels_in_paper").alias("num_side_channels"))
    )

    # --- Remove duplicates ---
    paper_info = df_data.select(["ID", "Title", "Year", "Conference"]).unique(subset=["ID"])

    # --- Add both covert-channel and side-channel count per paper in our corpus  ---
    summary_channel_per_paper = (
        paper_info
        .join(covert_per_paper_count, on="ID", how="left")
        .join(side_per_paper_count, on="ID", how="left")
        .fill_null(0)  # Replace missing counts with 0
        .with_columns([
            pl.col("num_covert_channels").cast(pl.Int32),
            pl.col("num_side_channels").cast(pl.Int32),
        ])
    )

    # --- Add the number of attacks in our corpus regarding covert and side channels ---
    summary_channel_per_paper= summary_channel_per_paper.with_columns(
        (pl.col("num_covert_channels") + pl.col("num_side_channels")).alias("total_channels")
    )

    summary_channel_per_paper.select(["Title", "Year", "Conference", "num_covert_channels", "num_side_channels", "total_channels"])
    return (summary_channel_per_paper,)


@app.cell
def _(mo, pl, summary_channel_per_paper):
    # --- Give the total number of attacks, side-channel attacks and covert-channel attacks ---

    result = pl.DataFrame({
        "Metric": [
            "Sum of Side Channels",
            "Sum of Covert Channels",
            "Sum of Channels",
        ],
        "Value": [
            summary_channel_per_paper["num_side_channels"].sum(),
            summary_channel_per_paper["num_covert_channels"].sum(),
            summary_channel_per_paper["total_channels"].sum(),
        ]
    })

    mo.ui.table(result)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r""" """)
    return


@app.cell
def _(df_data, pl):
    # Platforms to check directly from columns
    platform_cols = {
        "Intel": "Requirements per platform [Intel]",
        "AMD": "Requirements per platform [AMD]",
        "NVIDIA": "Requirements per platform [NVIDIA]",
        "ARM": "Requirements per platform [ARM]",
        "Apple": "Requirements per platform [Apple]",
    }

    # Detect from columns (non-empty means requirement exists)
    df_platforms = df_data.select([pl.col("Other requirement?")] + [
        pl.when(pl.col(col) != "")
          .then(pl.lit(1))
          .otherwise(pl.lit(0))
          .alias(platform)
        for platform, col in platform_cols.items()
    ])

    # Detect from "Other requirement?" column
    df_platforms = df_platforms.with_columns([
        (pl.col("Other requirement?").str.starts_with("GPU_").cast(pl.Int8()).alias("GPU")),
        (pl.col("Other requirement?").str.starts_with("iGPU_").cast(pl.Int8()).alias("iGPU")),
        (pl.col("Other requirement?").str.starts_with("RISC_").cast(pl.Int8()).alias("RISC")),
        (pl.col("Other requirement?").str.starts_with("TEE_").cast(pl.Int8()).alias("TEE")),
    ])
    return (df_platforms,)


@app.cell
def _(mo):
    mo.md(r"""# Types of platform benchmarked in our corpus.""")
    return


@app.cell
def _(df_data, df_platforms, mo, pl, px):
    # Total number of papers
    n_total = df_data.shape[0]

    # --- Per Platform (with constructors) ---

    # Count number of papers and percentage per platform
    platform_counts = (
        df_platforms.drop("Other requirement?")
        .sum()
        .transpose(include_header=True, header_name="Platform", column_names=["n_papers"])
        .with_columns([
            (pl.col("n_papers") / n_total * 100).round(1).alias("percentage")
        ])
        .with_columns([
            (pl.col("n_papers").cast(str) + " (" + pl.col("percentage").round(1).cast(str) + "%)").alias("label")
        ])
    )

    # Plot
    fig_platform = px.bar(
        platform_counts.to_pandas(),
        x="Platform",
        y="n_papers",
        title="Number and Percentage of Papers per Benchmarked Platform",
        text="label",
    )

    fig_platform.update_traces(textposition="outside")
    fig_platform.update_layout(
        yaxis_title="Number of Papers",
        xaxis_title="Platform",
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )

    mo.ui.plotly(fig_platform)
    return (n_total,)


@app.cell
def _(df_platforms, mo, n_total, pl, px):
    # --- Aggregated CPU/GPU/iGPU/TEE ---
    df_cpu_gpu = df_platforms.with_columns([
        (
            (pl.col("Intel") + pl.col("AMD") + pl.col("ARM") + pl.col("Apple") + pl.col("RISC") > 0)
            .cast(pl.Int8())
            .alias("CPU")
        )
    ])


    # --- Count number of papers and percentage per platform for aggregated platform only ---
    df_cpu_gpu = df_cpu_gpu.select(["CPU", "GPU", "iGPU", "TEE"])
    cpu_gpu_counts = (
        df_cpu_gpu.sum()
        .transpose(include_header=True, header_name="Category", column_names=["n_papers"])
        .with_columns([
            (pl.col("n_papers") / n_total * 100).round(1).alias("percentage")
        ])
        .with_columns([
            (pl.col("n_papers").cast(str) + " (" + pl.col("percentage").round(1).cast(str) + "%)").alias("label")
        ])
    )

    # Plot
    fig_cpu_gpu = px.bar(
        cpu_gpu_counts.to_pandas(),
        x="Category", y="n_papers", text="label",
        title="Number and Percentage of Papers per Category of Platform (CPU/GPU/iGPU/TEE)"
    )
    fig_cpu_gpu.update_traces(textposition="outside")
    fig_cpu_gpu.update_layout(yaxis_title="Number of Papers", xaxis_title="Category")

    mo.ui.plotly(fig_cpu_gpu)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Reproduction of Figures 4, 5, 7 and 15: "Distribution of the reported properties performed with covert- channel attacks or side-channel attack types", "Distribution of covert-channel reported properties among papers (Architecture conferences vs. Security conferences)" & "Distribution of papers that contain covert channels and side-channel attack types (Architecture conferences vs. Security conferences)."
    ## Covert channel reported properties.
    """
    )
    return


@app.cell
def _(Counter, combinations, final_covert_df, pl, px):
    # --- Get all unique reported properties combinations per paper ---
    comb_counter_solo = Counter() # Take combinations of combo including size 1
    comb_counter_len_part = Counter() # Take combinations of combo of maximal size per paper only
    comb_counter = Counter() # Take combinations of combo including size above 2 only

    # --- Create an "Others" group for one time assessment ---
    OTHERS_GROUP = {"Cache Miss Rate (%)", "Stability", "Raw Bit Accuracy considering the Bit Rate", "Sensitivity to Shared Array Size"}

    for assess_list in final_covert_df["How is it assessed?"].to_list():
        if isinstance(assess_list, str):
            part = [p.strip() for p in assess_list.split(";") if p.strip()]

            # Replace unwanted categories with "Other"
            cleaned_part = [
                ("Others" if p in OTHERS_GROUP else p)
                for p in part
            ]

            # Rename "Capacity (bandwith considering the error rate)" into "Capacity"
            renamed_part = [
                ("Capacity" if p == "Capacity (bandwith considering the error rate)" else p)
                for p in cleaned_part
            ]

            len_part = len(renamed_part)
            sorted_part = sorted(renamed_part)
            for combo_size in range(1, len_part + 1):
                if (combo_size == 1) :
                    for combo in combinations(sorted_part, combo_size):
                        comb_counter_solo[combo] += 1
                elif (combo_size == len_part) :
                    for combo in combinations(sorted_part, combo_size):
                        comb_counter_len_part[combo] += 1
                else :
                    for combo in combinations(sorted_part, combo_size):
                        comb_counter[combo] += 1

    # --- Helper: convert counter into Polars DataFrame ---
    def counter_to_df(counter):
        df = pl.DataFrame({
            "combo": [", ".join(c) for c in counter.keys()],
            "count": list(counter.values())
        })
        return df.sort("count", descending=True)

    # Convert to Polars DataFrame
    df_combos_solo = counter_to_df(comb_counter_solo)
    df_combos_len_part = counter_to_df(comb_counter_len_part)
    df_combos = counter_to_df(comb_counter)

    def make_plot_covert(df, title, x_name, y_name, x_label_rotation,
                         fig_width=1900, fig_height=900):
        # Compute percentages
        total = df["count"].sum()
        df = df.with_columns([
            ((df["count"] / total) * 100).round(1).alias("percentage"),
        ])
        df = df.with_columns([
            (df["count"].cast(str) + " (" + df["percentage"].cast(str) + "%)").alias("label_text")
        ])

        fig = px.bar(
            df.to_pandas(),
            x="combo",
            y="count",
            text="label_text",
            title=title
        )

        # ---------------------------
        # Layout: white background + black border + bold title + axis
        # ---------------------------
        fig.update_layout(
            width=fig_width,
            height=fig_height,
            font=dict(size=35, color="black", weight="bold"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(t=100, b=270, l=80, r=40),
        )

        # ---------------------------
        # Axes: black border on all sides, ticks, bold labels
        # ---------------------------
        fig.update_xaxes(
            title_text=x_name,
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror="ticks",  # mirrors axis lines on top and right
            ticks="outside",
            tickfont=dict(size=35, color="black", weight="bold"),
        )

        fig.update_yaxes(
            title_text=y_name,
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror="ticks",
            ticks="outside",
            tickfont=dict(size=35, color="black", weight="bold"),
            gridcolor="lightgray",
            range=[0, df["count"].max() * 1.2],  # extra vertical space
        )

        # ---------------------------
        # Bold text labels on top of bars
        # ---------------------------
        fig.update_traces(
            textposition="outside",
            textfont=dict(size=35, color="black", weight="bold")
        )

        # Optional: rotate x labels
        fig.update_xaxes(tickangle=x_label_rotation)

        # fig.write_image(title + ".pdf")
        fig.show()

    # --- Plots ---
    make_plot_covert(df_combos_solo, "Distribution of Covert-Channels Reported Properties", "Covert-Channels Reported Properties", "Number of Papers", 15)

    make_plot_covert(df_combos_len_part, "Distribution of  Most Common total Covert-Channels Reported Properties Combination", "Covert-Channels Reported Properties Combinations", "Number of Papers", 90, 3000, 2000)

    make_plot_covert(df_combos, "Distribution of  Most Common Covert-Channels Reported Properties Combination", "Covert-Channels Reported Properties Combinations", "Number of Papers", 90, 3000, 2000)
    return OTHERS_GROUP, counter_to_df, make_plot_covert


@app.cell
def _(px):
    def make_plot_grouped(df, title, x_name, y_name, legend_title, type, y_=None):
        # ---------------------------
        # Plotly bar chart
        # ---------------------------
        z = "n_papers"

        if (y_ != None):
            z = y_

        fig = px.bar(
            df,
            x="conf_group",
            y=z,
            color=type,
            barmode="group",
            title=title
        )
        # ---------------------------
        # Layout: white background + black border + bold font
        # ---------------------------
        fig.update_layout(
            width=1900,
            height=900,
            font=dict(size=35, color="black", weight="bold"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(t=100, b=230, l=80, r=40),
            legend=dict(title=dict(text=legend_title, font=dict(size=37, weight="bold"))),
        )

        # ---------------------------
        # X-axis styling
        # ---------------------------
        fig.update_xaxes(
            title_text=x_name,
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror="ticks",
            ticks="outside",
            tickfont=dict(size=35, color="black", weight="bold"),
        )

        # ---------------------------
        # Y-axis styling
        # ---------------------------
        max_y = df[z].max()

        fig.update_yaxes(
            title_text=y_name,
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror="ticks",
            ticks="outside",
            tickfont=dict(size=35, color="black", weight="bold"),
            gridcolor="lightgray"
        )

        # fig.write_image(title + ".pdf")
        return fig
    return (make_plot_grouped,)


@app.cell
def _(
    OTHERS_GROUP,
    archi_confs,
    final_covert_df,
    make_plot_grouped,
    pl,
    sec_confs,
):
    # --- Clean and explode the "How is it assessed?" column ---
    df_assess = (
        final_covert_df
        .with_columns(
            pl.col("How is it assessed?")
            .str.split(";")                      # split into list
            .alias("assess_list")
        )
        .explode("assess_list")
        .with_columns(pl.col("assess_list").str.strip_chars().alias("assess_type"))
        .filter(pl.col("assess_type").is_not_null())
    )

    # --- Count the number of paper per reported properties ---
    assess_count = (
        df_assess
        .group_by("assess_type")
        .agg(pl.len().alias("n_papers"))
        .sort("n_papers", descending=True)
    )

    # --- Differenciate result between type of conferences ---
    df_assess_grouped = (
        df_assess
        .with_columns(
            pl.when(pl.col("Conference").is_in(sec_confs)).then(pl.lit("Security"))
            .when(pl.col("Conference").is_in(archi_confs)).then(pl.lit("Architecture"))
            .otherwise(pl.lit("Others"))
            .alias("conf_group")
        )
        .with_columns(
            pl.when(pl.col("assess_type").is_in(OTHERS_GROUP)).then(pl.lit("Others"))
            .when(pl.col("assess_type") == "Capacity (bandwith considering the error rate)").
                then(pl.lit("Capacity"))
            .otherwise(pl.col("assess_type"))
            .alias("assess_type")
        )
    )

    # WARNING: Deduplicate (PaperID, assess_type) so each paper is counted ONCE per category
    df_unique = df_assess_grouped.unique(["Title", "conf_group", "assess_type"])

    # --- Count unique papers ---
    assess_conf_group = (
        df_unique
        .group_by(["conf_group", "assess_type"])
        .agg(pl.n_unique("Title").alias("n_papers"))
    )

    # --- Total number of papers per conference group ---
    total_papers = (
        df_unique.group_by("conf_group")
        .agg(pl.n_unique("Title").alias("total_papers"))
    )

    # --- Combined unique papers with their percentage of reported properties ---
    df_plot_covert = (
        assess_conf_group
        .join(total_papers, on="conf_group")
        .with_columns(
            (pl.col("n_papers") / pl.col("total_papers") * 100).round(2)
            .alias("percentage")
        )
    )

    df_plot_covert = df_plot_covert.sort("percentage", descending=True)
    df_plot_covert = df_plot_covert.to_pandas()

    # Plot
    fig_covert = make_plot_grouped(
        df_plot_covert,
        title="Reported Properties per Covert-Channel Paper per Conference Category",
        x_name="Conference Group",
        y_name="Percentage of Papers (%)",
        legend_title="",
        type="assess_type", 
        y_="percentage"
    )

    fig_covert.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Side channel attack types.""")
    return


@app.cell
def _(final_side_df, pl):
    # --- Clean the "What are they attacking?" column and count attacks ---
    df_attack = (
        final_side_df
        .with_columns(
            pl.col("What are they attacking?")
            .str.strip_chars()
            .alias("attack_type")
        )
        .filter(pl.col("attack_type").is_not_null())
    )

    # --- Count the number of paper per side-channel attack type ---
    attack_count = (
        df_attack
        .group_by("attack_type")
        .agg(pl.len().alias("n_papers"))
        .sort("n_papers", descending=True)
    )

    # --- Group all attacks per paper ---
    df_attack_groups = (
        final_side_df
        .group_by("Title")
        .agg(pl.col("What are they attacking?").drop_nulls().alias("attack_list"))
    )

    df_attack_groups
    return df_attack, df_attack_groups


@app.cell
def _(
    Counter,
    combinations,
    counter_to_df,
    df_attack_groups,
    make_plot_covert,
):
    # --- Get all unique reported properties combinations per paper ---
    comb_counter_side_solo = Counter() # Take combinations of combo including size 1
    comb_counter_side_len_part = Counter() # Take combinations of combo of maximal size per paper only
    comb_counter_side = Counter() # Take combinations of combo including size above 2 only

    for attack_list in df_attack_groups["attack_list"].to_list():
        PART = sorted(set([
            "Others" if pt.strip().startswith("Other_") else pt.strip()
            for pt in attack_list if pt and isinstance(pt, str)
        ]))

        # Rename "Crypto - CF-based (e.g. mod exp / ECDSA / ECSM) - known vulnerability" into "Crypto - CF-based"
        renamed_CF_part = [
            ("Crypto - CF-based" if p == "Crypto - CF-based (e.g. mod exp / ECDSA / ECSM) - known vulnerability" else p)
            for p in PART
        ]

        # Rename "Crypto - memory access-based (e.g. AES T-table) - known vulnerability" into "Crypto - memory access-based"
        renamed_memory_part = [
            ("Crypto - memory access-based" if p == "Crypto - memory access-based (e.g. AES T-table) - known vulnerability" else p)
            for p in renamed_CF_part
        ]

        # Rename "Breaking constant-time cryptography" into "Breaking CT crypto"
        renamed_CT_part = [
            ("Breaking CT crypto" if p == "Breaking constant-time cryptography" else p)
            for p in renamed_memory_part
        ]

        len_side_part = len(renamed_CT_part)
        if len_side_part == 0:
            continue

        # loop over all combination sizes
        for combo_side_size in range(1, len_side_part + 1):
            if combo_side_size == 1:
                for combos in combinations(renamed_CT_part, combo_side_size):
                    comb_counter_side_solo[combos] += 1
            elif combo_side_size == len_side_part:
                for combos in combinations(renamed_CT_part, combo_side_size):
                    comb_counter_side_len_part[combos] += 1
            else:
                for combos in combinations(renamed_CT_part, combo_side_size):
                    comb_counter_side[combos] += 1           

    # # --- Apply transformation ---
    df_combos_side_solo = counter_to_df(comb_counter_side_solo)
    df_combos_side_len_part = counter_to_df(comb_counter_side_len_part)
    df_combos_side = counter_to_df(comb_counter_side)

    # --- Plots ---
    make_plot_covert(df_combos_side_solo, "Distribution of Side-Channel Attack Types", "Side-Channel Attack Types", "Number of Papers", 15)

    make_plot_covert(df_combos_side_len_part, "Distribution of Most Common Total Side-Channel Attack Types Combination", "Side-Channel Attack Types Combination", "Number of Papers", 90, 3000, 2000)

    make_plot_covert(df_combos_side, "Distribution of  Most Common Side-Channel Attack Types Combination", "Side-Channel Attack Types Combination", "Number of Papers", 90, 3000, 2000)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r""" """)
    return


@app.cell
def _(
    archi_confs,
    df_attack,
    final_side_df,
    make_plot_grouped,
    pl,
    sec_confs,
    summary_channel_per_paper,
):
    # --- Group papers into Security / Architecture / Others ---
    papers_group = (
        final_side_df
        .with_columns(
            pl.when(pl.col("Conference").is_in(sec_confs))
            .then(pl.lit("Security"))
            .when(pl.col("Conference").is_in(archi_confs))
            .then(pl.lit("Architecture"))
            .otherwise(pl.lit("Others"))
            .alias("conf_group")
        )
        .select(["Title", "conf_group"])
        .unique()
    )


    # --- Add conf_group to attack dataframe ---
    df_attack_grouped = (
        df_attack
        .with_columns(
            pl.when(pl.col("Conference").is_in(sec_confs))
            .then(pl.lit("Security"))
            .when(pl.col("Conference").is_in(archi_confs))
            .then(pl.lit("Architecture"))
            .otherwise(pl.lit("Others"))
            .alias("conf_group")
        )
    )


    # --- Count side-channel attacks per paper and category ---
    side_channel_per_paper = (
        df_attack_grouped
        .with_columns([
            pl.when(pl.col("attack_type") == "Crypto - CF-based (e.g. mod exp / ECDSA / ECSM) - known vulnerability")
              .then(pl.lit("Crypto - CF-based"))
              .when(pl.col("attack_type") == "Crypto - memory access-based (e.g. AES T-table) - known vulnerability")
              .then(pl.lit("Crypto - memory access-based"))
              .when(pl.col("attack_type") == "Breaking constant-time cryptography")
              .then(pl.lit("Breaking CT crypto"))
              .otherwise(pl.col("attack_type"))
              .alias("attack_type")
        ])
        .with_columns(
            pl.when(pl.col("attack_type").str.starts_with("Other_"))
              .then(pl.lit("Others"))
              .otherwise(pl.col("attack_type"))
              .alias("category")
        )
        .select(["Title", "conf_group", "category"])
        .unique(["Title", "category"])
        .group_by(["conf_group", "category"])
        .agg(pl.len().alias("n_papers"))
    )

    # --- Keep only useful columns ---
    side_channel_per_paper = (
        side_channel_per_paper
        .select(["conf_group", "category", "n_papers"])
    )


    # --- List all papers with ≥1 covert channel ---
    covert_df = (
        summary_channel_per_paper
        .filter(pl.col("num_covert_channels") > 0)
        .select(["Title"])
        .unique()
    )

    # --- Count covert-channel papers per conference group ---
    covert_group = (
        covert_df
        .join(papers_group, on="Title", how="left")
        .group_by("conf_group")
        .agg(pl.len().alias("n_papers"))
        .with_columns([
            pl.lit("Covert channel").alias("category")
        ])
        .select(["conf_group", "category", "n_papers"])
    )


    # --- Combine side-channel and covert counts ---
    combined = pl.concat([
        side_channel_per_paper,
        covert_group
    ])


    # --- Total number of papers per conference group ---
    totals_ = papers_group.group_by("conf_group").agg(
        pl.len().alias("total_papers")
    )


    # --- Compute percentages per category and group ---
    combined_pct = (
        combined
        .join(totals_, on="conf_group", how="left")
        .with_columns(
            (pl.col("n_papers") * 100 / pl.col("total_papers"))
            .round(2)
            .alias("percentage")
        )
        .select(["conf_group", "category", "percentage"])
    )


    # --- Convert to pandas for plotting ---
    df_plot_ = combined_pct.to_pandas()


    # --- Ordering rules for categories ---
    order = {
        "Covert channel": 0,
        "Crypto - CF-based": 1,
        "Crypto - memory access-based": 2,
        "Breaking CT crypto": 3,
        "Fingerprinting": 4,
        "(Inter)keystroke recovery": 5,
        "Toy example / Microbenchmark": 6,
        "(K)ASLR break": 7, 
        "Breaking CT crypto": 8, 
        "Pixel stealing": 9,
        "Deep Learning parameters": 10,
        "Others": 11
    }

    df_plot_["sort_order"] = df_plot_["category"].map(order)
    df_plot_ = df_plot_.sort_values(["conf_group", "sort_order"])


    # --- Plot grouped percentage chart ---
    fig_side_attack = make_plot_grouped(
        df_plot_,
        title="Type of Side or Covert Channels per Paper (Architecture vs. Security)",
        x_name="Conference Group",
        y_name="Percentage of Papers (%)",
        legend_title="",
        type="category", 
        y_="percentage"
    )

    fig_side_attack.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# List of usual targets for side-channel attacks.""")
    return


@app.cell
def _(final_side_df, pl):
    # We define the categories to keep, because they are the one of interest
    attack_categories = [
        "Fingerprinting",
        "Crypto - CF-based (e.g. mod exp / ECDSA / ECSM) - known vulnerability",
        "Crypto - memory access-based (e.g. AES T-table) - known vulnerability",
    ]

    # Filter and select only the needed columns
    df_target_version = (
        final_side_df
        .filter(pl.col("What are they attacking?").is_in(attack_categories))
        .select(["What are they attacking?", "Is the target version specified?"])
    )

    df_target_version
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Crypto - CF-based (e.g. mod exp / ECDSA / ECSM) - known vulnerability (41 attacks)

    - GnuPG v1.4.13 (7 times), v1.4.14 + 1 unknown version,
    - GnuPG libgcrypt v1.6.3 (5 times), v1.5.2 (3 times), v1.5.0 and v1.7.5, 
    - OpenSSL v1.1.0h (2 times), v1.0.2e,  v1.0.1e, v1.1.1h, v3.2

    are the most common targeted victims.

    ### Fingerprinting (23 attacks)

    - Alexa top 100 websites (3 times),
    - Chrome v63.0.3239.84 (2 times), v103.0.5060.114 and v121.0

    are the most common targeted victims.

    ### Crypto - memory access-based (e.g. AES T-table) - known vulnerability (17 attacks)

    - OpenSSL v1.0.1e (5 times), v1.0.1f (2 times), v0.9.8, v0.9.8b, v1.1.0g and v1.0.2 + 2 unknown versions

    are the most common targeted victims.

    ### Worth mentioning 

    - MbedTLS v1.3.10, v2.5, v2.6, v2.7, v2.13.0, v2.14, v2.15, v2.16, v2.28, v3.0.0, v3.0 (2 times), v3.1, v3.4.0 + 1 unknown version,
    - GCC v7.5, v8.4, v9.4, v10.3,
    - WolfSSL v4.2.0, v5.6.4.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Reproduction of Figures 8 and 9: Distribution of flawed (fully or partially) per years per papers (all conferences, architecture only and security only).

    NOTA BENE: The tables of data can be found in the summary.html file associated with this artifact.
    """
    )
    return


@app.cell
def _(Patch, plt):
    # --- Years used in all plots ---
    years_ = [2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024]


    # --- Helper function: build boxplot (bxp) dictionaries from arrays ---

    def make_bxp_dict(mins, q1, med, q3, maxs):
        return [
            {"whislo": mins[i], "q1": q1[i], "med": med[i], "q3": q3[i], "whishi": maxs[i]}
            for i in range(len(mins))
        ]


    # --- Custom mustache (boxplot) function for three then two datasets ---

    def mustache_plot_3param(data_1, data_2, data_3, y_label, title, leg1, leg2, leg3):
        # --- Create plot ---
        fig_, ax = plt.subplots(figsize=(16, 10))

        # --- Horizontal offsets (side-by-side boxplots) ---
        positions1 = [i - 0.25 for i in range(1, len(years_) + 1)]
        positions2 = [i         for i in range(1, len(years_) + 1)]
        positions3 = [i + 0.25 for i in range(1, len(years_) + 1)]

        # --- Plot dataset 1 ---
        ax.bxp(
            data_1, positions=positions1, widths=0.20, showfliers=False,
            boxprops=dict(color="C0"), medianprops=dict(color="C0"),
            whiskerprops=dict(color="C0"), capprops=dict(color="C0")
        )

        # --- Plot dataset 2 ---
        ax.bxp(
            data_2, positions=positions2, widths=0.20, showfliers=False,
            boxprops=dict(color="C1"), medianprops=dict(color="C1"),
            whiskerprops=dict(color="C1"), capprops=dict(color="C1")
        )

        # --- Plot dataset 3 ---
        ax.bxp(
            data_3, positions=positions3, widths=0.20, showfliers=False,
            boxprops=dict(color="C2"), medianprops=dict(color="C2"),
            whiskerprops=dict(color="C2"), capprops=dict(color="C2")
        )

        # --- Formatting / labels ---
        ax.set_xticks(range(1, len(years_) + 1))
        ax.set_xticklabels(years_, fontsize=25)
        ax.set_xlabel("Year", fontsize=30)
        ax.set_ylabel(y_label, fontsize=28)
        ax.set_title(title.replace("_", " ").title(), fontsize=28)

        # --- Legend ---
        legend_handles = [
            Patch(color="C0", label=leg1),
            Patch(color="C1", label=leg2),
            Patch(color="C2", label=leg3)
        ]
        ax.legend(handles=legend_handles, loc="upper left", fontsize=22)

        ax.tick_params(axis='both', which='major', labelsize=22)

        plt.tight_layout()
        # plt.savefig(title + ".pdf")
        plt.show()


    def mustache_plot_2param(data_1, data_2, y_label, title, leg1, leg2):
        # === Create plot ===
        fig_, ax = plt.subplots(figsize=(16, 10))

        # Horizontal offsets
        positions1 = [i - 0.25 for i in range(1, len(years_) + 1)]
        positions2 = [i         for i in range(1, len(years_) + 1)]

        # === Plot two datasets ===
        ax.bxp(
            data_1, positions=positions1, widths=0.20, showfliers=False,
            boxprops=dict(color="C0"), medianprops=dict(color="C0"),
            whiskerprops=dict(color="C0"), capprops=dict(color="C0")
        )
        ax.bxp(
            data_2, positions=positions2, widths=0.20, showfliers=False,
            boxprops=dict(color="C1"), medianprops=dict(color="C1"),
            whiskerprops=dict(color="C1"), capprops=dict(color="C1")
        )

        # === Formatting ===
        ax.set_xticks(range(1, len(years_) + 1))
        ax.set_xticklabels(years_, fontsize=25)
        ax.set_xlabel("Year", fontsize=30)
        ax.set_ylabel(y_label, fontsize=22)
        ax.set_title(title.replace("_", " ").title(), fontsize=28)

        # === Legend ===
        legend_handles = [
            Patch(color="C0", label=leg1),
            Patch(color="C1", label=leg2),
        ]
        ax.legend(handles=legend_handles, loc="upper left", fontsize=25, ncol=2)

        # Increase tick label sizes
        ax.tick_params(axis='both', which='major', labelsize=22)

        plt.tight_layout()

        # plt.savefig(title + ".pdf")
        plt.show()
    return make_bxp_dict, mustache_plot_2param, mustache_plot_3param


@app.cell
def _(make_bxp_dict, mustache_plot_2param):
    # --- FLAWED PAPERS (ALL CONFERENCES) ---

    # === Flawed ===
    min1  = [4,1,3,2,1,0,0,0,0,0,0]
    q1_1  = [4,1.75,3,3,3.5,2.25,0.25,1,2,2,2.5]
    med1  = [4,2,3.5,4,6,3.5,0.5,2.5,3,3,4]
    q3_1  = [4,2.5,5.25,5,6,5,0.75,4,4,4,6.5]
    max1  = [4,4,9,5,7,8,1,9,8,6,10]

    # === Partially flawed ===
    min2  = [1,2,0,0,0,0,2,0,1,0,1]
    q1_2  = [1,2,0.75,0,1.5,0.75,2.75,1,1,1,1.5]
    med2  = [1,2.5,1,1,3,1,3.5,1,3,3,2]
    q3_2  = [1,3.25,1.75,1,3,1.25,4.25,2.75,3,3.25,2.5]
    max2  = [1,4,4,2,4,2,5,5,5,5,6]

    data1_f = make_bxp_dict(min1, q1_1, med1, q3_1, max1)
    data2_f = make_bxp_dict(min2, q1_2, med2, q3_2, max2)

    mustache_plot_2param(
        data1_f, data2_f,
        "Number of Flaws and Partial Flaws per Paper",
        "flawed_papers_all_conferences",
        "Flaws", "Partial Flaws"
    )

    # --- ARCHITECTURE CONFERENCES -----

    # === Flawed ===
    min1  = [0, 0, 9, 3, 4, 4, 1, 1, 0, 3, 0]
    q1_1  = [0, 0, 9, 3, 4.5, 4, 1, 3.25, 3, 3.75, 4.5]
    med1  = [0, 0, 9, 3, 5, 4, 1, 4, 4, 4, 7]
    q3_1  = [0, 0, 9, 3, 5.5, 4, 1, 5.5, 4, 4, 7]
    max1  = [0, 0, 9, 3, 6, 4, 1, 9, 8, 4, 10]

    # === Partially flawed ===
    min2  = [0, 0, 1, 0, 0, 2, 2, 0, 1, 1, 2]
    q1_2  = [0, 0, 1, 0, 0.25, 2, 2, 1, 1, 2.5, 2]
    med2  = [0, 0, 1, 0, 0.5, 2, 2, 1, 3, 3.5, 3]
    q3_2  = [0, 0, 1, 0, 0.75, 2, 2, 1, 3, 4, 3.5]
    max2  = [0, 0, 1, 0, 1, 2, 2, 5, 3, 4, 6]

    data1_micro_f = make_bxp_dict(min1, q1_1, med1, q3_1, max1)
    data2_micro_f = make_bxp_dict(min2, q1_2, med2, q3_2, max2)

    mustache_plot_2param(
        data1_micro_f, data2_micro_f,
        "Number of Flaws and Partial Flaws per Paper",
        "flawed_papers_architecture_conferences",
        "Flaws", "Partial Flaws"
    )

    # --- SECURITY CONFERENCES ---

    # === Flawed ===
    min1  = [4, 1, 3, 2, 1, 0, 0, 0, 1, 0, 2]
    q1_1  = [4, 1.75, 3, 3.5, 3, 1.5, 0, 0.75, 2, 2, 2]
    med1  = [4, 2, 3, 4.5, 6, 3, 0, 1, 3, 2, 3]
    q3_1  = [4, 2.5, 3.5, 5, 6, 5.5, 0, 1.25, 3.75, 3, 4.25]
    max1  = [4, 4, 4, 5, 7, 8, 0, 2, 7, 6, 5]


    # === Partially flawed ===
    min2  = [1, 2, 0, 0, 2, 0, 5, 1, 1, 0, 1]
    q1_2  = [1, 2, 0.5, 0.75, 3, 0.5, 5, 1.75, 1.5, 1, 1]
    med2  = [1, 2.5, 1, 1, 3, 1, 5, 2.5, 3, 2.5, 1.5]
    q3_2  = [1, 3.25, 2.5, 1.25, 3, 1, 5, 3, 3.75, 3, 2]
    max2  = [1, 4, 4, 2, 4, 1, 5, 3, 5, 5, 2]

    data1_secu_f = make_bxp_dict(min1, q1_1, med1, q3_1, max1)
    data2_secu_f = make_bxp_dict(min2, q1_2, med2, q3_2, max2)

    mustache_plot_2param(
        data1_secu_f, data2_secu_f,
        "Number of Flaws and Partial Flaws per Paper",
        "flawed_papers_security_conferences",
        "Flaws", "Partial Flaws"
    )
    return


@app.cell
def _(mo):
    mo.md(r"""# Reproduction of Figure 11: Distribution of the number of configuration evaluated per years per papers (all conferences, architecture only and security only).""")
    return


@app.cell
def _(
    all_years,
    archi_confs,
    compute_boxplot_stats,
    df_data,
    make_bxp_dict_eval,
    mustache_plot_3param,
    pl,
    sec_confs,
):

    # --- Select relevant columns ---
    df_config = df_data.select([
        "Title",
        "Year",
        "Conference",
        "Number of configuration evaluated",
        "Number of configuration evaluated_duplicated_0",
        "Number of configuration evaluated_duplicated_1",
        "Number of platform evaluated_duplicated_0",
        "Number of platform evaluated_duplicated_1",
        "Number of platform evaluated_duplicated_2",
        "Number of platform evaluated_duplicated_3",
        "Number of platform evaluated_duplicated_4",
    ])


    # --- Normalize numeric fields (replace "" → null → 0) ---
    config_cols = [
        "Number of configuration evaluated",
        "Number of configuration evaluated_duplicated_0",
        "Number of configuration evaluated_duplicated_1",
        "Number of platform evaluated_duplicated_0",
        "Number of platform evaluated_duplicated_1",
        "Number of platform evaluated_duplicated_2",
        "Number of platform evaluated_duplicated_3",
        "Number of platform evaluated_duplicated_4",
    ]

    for c_ in config_cols:
        df_config = df_config.with_columns(
            pl.col(c_)
            .cast(pl.Utf8)                 
            .str.strip_chars()             
            .replace("", None)             
            .cast(pl.Float64, strict=False) 
            .fill_null(0)                  
            .alias(c_)
        )


    # --- Compute total configurations per paper ---
    df_config = df_config.with_columns(
        pl.sum_horizontal([pl.col(c) for c in config_cols]).alias("total_configurations")
    )


    # --- Add conf_group column (Security / Architecture / Other) ---
    df_config = df_config.with_columns(
        pl.when(pl.col("Conference").is_in(sec_confs))
          .then(pl.lit("Security"))
          .when(pl.col("Conference").is_in(archi_confs))
          .then(pl.lit("Architecture"))
          .otherwise(pl.lit("Other"))
          .alias("conf_group")
    )


    # --- Split into groups ---
    df_config_all  = df_config
    df_config_sec  = df_config.filter(pl.col("conf_group") == "Security")
    df_config_arch = df_config.filter(pl.col("conf_group") == "Architecture")


    # --- Compute boxplot statistics ---
    stats_config_all = compute_boxplot_stats(df_config_all,  "total_configurations", all_years)
    stats_config_sec = compute_boxplot_stats(df_config_sec,  "total_configurations", all_years)
    stats_config_arch = compute_boxplot_stats(df_config_arch, "total_configurations", all_years)

    data_config_all  = make_bxp_dict_eval(stats_config_all)
    data_config_sec  = make_bxp_dict_eval(stats_config_sec)
    data_config_arch = make_bxp_dict_eval(stats_config_arch)


    # --- Final Figure ---
    figure_configuration_per_year = mustache_plot_3param(
        data_config_sec,
        data_config_arch,
        data_config_all,
        "Number of Configurations per Paper",
        "number_of_benchmarked_configuration_per_year",
        "Security Conferences",
        "Architecture Conferences",
        "All Conferences"
    )
    return


@app.cell
def _(mo):
    mo.md(r"""# Reproduction of Figure 10: Distribution of the number of platform evaluated per years per papers (all conferences, architecture only and security only).""")
    return


@app.cell
def _(
    all_years,
    archi_confs,
    compute_boxplot_stats,
    df_data,
    make_bxp_dict_eval,
    mustache_plot_3param,
    pl,
    sec_confs,
):
    # Base selection
    df_platform = df_data.select([
        "Year",
        "Conference",
        "Number of platform evaluated"
    ])

    # Assign conference group
    df_platform = df_platform.with_columns([
        pl.when(pl.col("Conference").is_in(sec_confs))
          .then(pl.lit("Security"))
          .when(pl.col("Conference").is_in(archi_confs))
          .then(pl.lit("Architecture"))
          .otherwise(pl.lit("Other"))
          .alias("conf_group")
    ])

    # Filter dataframes by group of conference
    df_platform_all  = df_platform
    df_platform_sec  = df_platform.filter(pl.col("conf_group") == "Security")
    df_platform_arch = df_platform.filter(pl.col("conf_group") == "Architecture")

    # Compute statistics
    stats_platform_all  = compute_boxplot_stats(df_platform_all,  "Number of platform evaluated", all_years)
    stats_platform_sec  = compute_boxplot_stats(df_platform_sec,  "Number of platform evaluated", all_years)
    stats_platform_arch = compute_boxplot_stats(df_platform_arch, "Number of platform evaluated", all_years)

    # Convert stats to dicts for plotting
    data_platform_all  = make_bxp_dict_eval(stats_platform_all)
    data_platform_sec  = make_bxp_dict_eval(stats_platform_sec)
    data_platform_arch = make_bxp_dict_eval(stats_platform_arch)

    # Plot
    figure_platform_per_year = mustache_plot_3param(
        data_platform_sec,
        data_platform_arch,
        data_platform_all,
        "Number of Tested Platforms per Paper",
        "Number of Platform Evaluated per Year",
        "Security Conferences",
        "Architecture Conferences",
        "All Conferences"
    )

    figure_platform_per_year
    return


@app.cell
def _(mo):
    mo.md(r"""# Reproduction of Figures 12, 13 and 14: Distribution of the number of Benchmark per years per papers (all conferences, architecture only and security only).""")
    return


@app.cell
def _(
    archi_confs,
    mustache_plot_3param,
    pl,
    sec_confs,
    summary_channel_per_paper,
):
    # --- Keep only relevant evaluation columns ---
    df_ = summary_channel_per_paper.select([
        "Year", "Conference", 
        "num_covert_channels", 
        "num_side_channels", 
        "total_channels"
    ])

    # --- Add conference group label (Security / Architecture / Other) ---
    df_ = df_.with_columns(
        pl.when(pl.col("Conference").is_in(sec_confs))
          .then(pl.lit("Security"))
          .when(pl.col("Conference").is_in(archi_confs))
          .then(pl.lit("Architecture"))
          .otherwise(pl.lit("Other"))
          .alias("conf_group")
    )

    # --- Sort list of all years (x-axis reference) ---
    all_years = sorted(df_["Year"].unique().to_list())

    # --- Compute per-year boxplot statistics for one metric ---
    def compute_boxplot_stats(df_, value_column, all_years):
        stats = {"Min": [], "Q1": [], "Median": [], "Q3": [], "Max": []}

        for year in all_years:
            values = df_.filter(pl.col("Year") == year).select(value_column).to_series()

            if len(values) == 0:
                stats["Min"].append(0)
                stats["Q1"].append(0)
                stats["Median"].append(0)
                stats["Q3"].append(0)
                stats["Max"].append(0)
            else:
                stats["Min"].append(values.min())
                stats["Q1"].append(values.quantile(0.25))
                stats["Median"].append(values.median())
                stats["Q3"].append(values.quantile(0.75))
                stats["Max"].append(values.max())

        return stats

    # --- Compute global evaluation statistics (all conferences) ---
    covert_stats = compute_boxplot_stats(df_, "num_covert_channels", all_years)
    side_stats   = compute_boxplot_stats(df_, "num_side_channels", all_years)
    total_stats  = compute_boxplot_stats(df_, "total_channels", all_years)

    # --- Convert stats to matplotlib bxp dict format ---
    def make_bxp_dict_eval(stats):
        return [
            {
                "whislo":  stats["Min"][i],
                "q1":      stats["Q1"][i],
                "med":     stats["Median"][i],
                "q3":      stats["Q3"][i],
                "whishi":  stats["Max"][i]
            }
            for i in range(len(stats["Min"]))
        ]

    # --- Build bxp lists for all-conference plot ---
    data_covert = make_bxp_dict_eval(covert_stats)
    data_side   = make_bxp_dict_eval(side_stats)
    data_total  = make_bxp_dict_eval(total_stats)

    # --- Plot: evaluations per year (all conferences) ---
    figure_evaluations_per_year = mustache_plot_3param(
        data_covert, data_side, data_total,
        "Number of Benchmarks per Paper",
        "Benchmark Counts per Paper Over Time (All Conferences)",
        "Covert-channel Benchmarks",
        "Side-channel Benchmarks",
        "Total Benchmarks"
    )

    # --- Filter Security group only ---
    df_security = df_.filter(pl.col("conf_group") == "Security")

    # --- Compute stats for security conferences ---
    covert_stats_security = compute_boxplot_stats(df_security, "num_covert_channels", all_years)
    side_stats_security   = compute_boxplot_stats(df_security, "num_side_channels", all_years)
    total_stats_security  = compute_boxplot_stats(df_security, "total_channels", all_years)

    # --- Build bxp lists for security-only plot ---
    data_covert_security = make_bxp_dict_eval(covert_stats_security)
    data_side_security   = make_bxp_dict_eval(side_stats_security)
    data_total_security  = make_bxp_dict_eval(total_stats_security)

    # --- Plot: evaluations per year (security conferences) ---
    figure_evaluations_per_year_security = mustache_plot_3param(
        data_covert_security, data_side_security, data_total_security,
        "Number of Benchmarks per Paper",
        "Benchmark Counts per Paper Over Time (Security Conferences)",
        "Covert-channel Benchmarks",
        "Side-channel Benchmarks",
        "Total Benchmarks"
    )

    # --- Filter Architecture group only ---
    df_microarchitecture = df_.filter(pl.col("conf_group") == "Architecture")

    # --- Compute stats for architecture conferences ---
    covert_stats_microarchitecture = compute_boxplot_stats(df_microarchitecture, "num_covert_channels", all_years)
    side_stats_microarchitecture   = compute_boxplot_stats(df_microarchitecture, "num_side_channels", all_years)
    total_stats_microarchitecture  = compute_boxplot_stats(df_microarchitecture, "total_channels", all_years)

    # --- Build bxp lists for architecture-only plot ---
    data_covert_microarchitecture = make_bxp_dict_eval(covert_stats_microarchitecture)
    data_side_microarchitecture   = make_bxp_dict_eval(side_stats_microarchitecture)
    data_total_microarchitecture  = make_bxp_dict_eval(total_stats_microarchitecture)

    # --- Plot: evaluations per year (architecture conferences) ---
    figure_evaluations_per_year_microarchitecture = mustache_plot_3param(
        data_covert_microarchitecture,
        data_side_microarchitecture,
        data_total_microarchitecture,
        "Number of Benchmarks per Paper",
        "Benchmark Counts per Paper Over Time (Architecture Conferences)",
        "Covert-channel Benchmark",
        "Side-channel Benchmark",
        "All Benchmark"
    )
    return all_years, compute_boxplot_stats, make_bxp_dict_eval


if __name__ == "__main__":
    app.run()
