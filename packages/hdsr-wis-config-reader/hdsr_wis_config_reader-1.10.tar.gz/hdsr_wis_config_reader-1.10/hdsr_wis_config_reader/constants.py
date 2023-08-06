from pathlib import Path


# Handy constant for building relative paths
BASE_DIR = Path(__file__).parent

if BASE_DIR.name != "hdsr_wis_config_reader":
    raise AssertionError(
        f"BASE_DIR {BASE_DIR.name} must be project name 'hdsr_wis_config_reader'"
    )

WIS_CONFIG_TEST_DIR = BASE_DIR / "tests" / "data" / "input" / "config_wis60prd_202002"

# GITHUB WIS CONFIG (only for testing)
GITHUB_ORGANISATION_NAME = "hdsr-mid"
GITHUB_WIS_CONFIG_REPO_NAME = "FEWS-WIS_HKV"
GITHUB_WIS_CONFIG_BRANCH_NAME = "202002-prd"


GITHUB_STARTENDDATE_REPO_NAME = "startenddate"
GITHUB_STARTENDDATE_BRANCH_NAME = "main"
GITHUB_STARTENDDATE_CAW_OPPERVLAKTEWATER_SHORT = Path(
    "data/output/results/caw_oppervlaktewater_short.csv"
)
GITHUB_STARTENDDATE_CAW_OPPERVLAKTEWATER_LONG = Path(
    "data/output/results/caw_oppervlaktewater_long.csv"
)
GITHUB_STARTENDDATE_CAW_OPPERVLAKTEWATER_HYMOS_SHORT = Path(
    "data/output/results/caw_oppervlaktewater_hymos_short.csv"
)
