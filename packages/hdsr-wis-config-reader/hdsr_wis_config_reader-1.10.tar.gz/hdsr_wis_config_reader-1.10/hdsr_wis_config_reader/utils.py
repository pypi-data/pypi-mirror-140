from hdsr_wis_config_reader.idmappings.columns import IdMapColumnChoices
from hdsr_wis_config_reader.idmappings.columns import ExLocChoices
from hdsr_wis_config_reader.idmappings.columns import StartEndDateColumnChoices
from hdsr_wis_config_reader.idmappings.custom_dataframe import IdMappingDataframe
from hdsr_wis_config_reader.idmappings.files import IdMapChoices

import logging
import numpy as np
import pandas as pd  # noqa


logger = logging.getLogger(__name__)


def merge_startenddate_idmap(
    df_idmap: IdMappingDataframe,
    df_startenddate: pd.DataFrame,
) -> pd.DataFrame:
    """Add 5 idmap columns ('ex_loc', 'ex_par', 'int_loc', 'int_par', ídmap_source') to df_startenddate."""
    logger.info("merging startendate csv with idmapping xml")

    # check args
    assert sorted(df_startenddate.columns) == sorted(StartEndDateColumnChoices.get_all())
    assert isinstance(df_idmap, IdMappingDataframe)

    int_loc = IdMapColumnChoices.int_loc.value
    int_par = IdMapColumnChoices.int_par.value
    ex_loc = IdMapColumnChoices.ex_loc.value
    ex_par = IdMapColumnChoices.ex_par.value
    idmap_source = "idmap_source"
    # from '8808_IB1' to '8808' and 'IB1'
    df_startenddate[[ex_loc, ex_par]] = df_startenddate[StartEndDateColumnChoices.series.value].str.split(
        pat="_", n=1, expand=True
    )
    int_loc_collector = []
    int_par_collector = []
    idmap_source_collector = []

    # Create a list of dictionaries in which each dictionary corresponds to an input data row
    for _, row in df_startenddate.iterrows():
        filter_df = df_idmap.get_filtered_df(
            ex_loc=row[ex_loc],
            ex_par=row[ex_par],
        )
        if filter_df.empty:
            int_loc_collector.append([""])
            idmap_source_collector.append("")
            int_par_collector.append("")
            continue
        idmap_intlocs = filter_df[int_loc].to_list()
        nr_int_locs = len(idmap_intlocs)
        if nr_int_locs > 1:
            # raise an error, except for 2 cornercases:
            # 1) stuurpeil
            #    the combo {ex_par, ex_loc} should be unique, except for 'stuurpeil': soms wordt een
            #    stuurpeil aan meerdere interne (verschillende) locaties wordt gekoppeld. Bijv 1
            #    stuurpeil voor 2 pompen, of 2 stuwen, of 2 schuiven
            # 2) opgesplitste locatie
            # TODO: verfiy with Roger:
            #  zijn er 1 of twee uitzonderingen op "the combo {ex_par, ex_loc} should be unique" ?
            #  1) stuurpeil (hierboven)
            #  2) opgesplitste locaties dan? zoals:
            # noqa <map externalLocation="2805" externalParameter="HS2" internalLocation="KW219120" internalParameter="H.S.0"/>
            # noqa <map externalLocation="2805" externalParameter="HS2" internalLocation="KW219130" internalParameter="H.S.0"/>
            # noqa als opgesplitste locatie ook uitzondering is, kunnen we deze verder specificeren (bijv alleen met streefpeil)
            is_stuurpeil_loc = row[ex_par].startswith("HR")
            is_split_loc = ExLocChoices.is_split(ex_loc=row[ex_loc])
            is_unique_int_loc = len(set(idmap_intlocs)) == 1
            is_only_in_hymos_and_idopvl_water = sorted(set(filter_df["source"])) == [
                IdMapChoices.idmap_opvl_water.value,
                IdMapChoices.idmap_opvl_water_hymos.value,
            ]
            exceptions = (
                is_stuurpeil_loc,
                is_split_loc,
                is_unique_int_loc,
                is_only_in_hymos_and_idopvl_water,
            )
            if not any(exceptions):
                msg = (
                    f"cannot continue, fix this first as multi int_locs are not allowed: found {nr_int_locs}"
                    f" int_locs {idmap_intlocs} in idmap with (ex_loc={row[ex_loc]}, ex_par={row[ex_par]})"
                )
                raise AssertionError(msg)

        # example after 4 iterations:
        # int_loc_collector =  [[''], [''], ['KW100111', 'KW100111'], ['OW100102', 'OW100102']]
        # idmap_source_collector = ['', '', 'IdOPVLWATER', 'IdOPVLWATER_HYMOS', 'IdOPVLWATER', 'IdOPVLWATER_HYMOS']
        int_loc_collector.append(idmap_intlocs)
        [int_par_collector.append(x) for x in filter_df[int_par].to_list()]
        [idmap_source_collector.append(x) for x in filter_df["source"].to_list()]

    assert len(df_startenddate) == len(int_loc_collector) != len(idmap_source_collector) == len(int_par_collector)
    df_startenddate[int_loc] = int_loc_collector
    # Example explode nested columns to rows
    # df = pd.DataFrame({'A': [1, 2, 3, 4],'B': [[1, 2], [1, 2], [], np.nan]})
    #           A       B
    #        0  1  [1, 2]
    #        1  3      []
    #        2  4     NaN
    # df = df.explode('B')
    #           A       B
    #        0  1       1
    #        0  1       2
    #        1  3     NaN
    #        2  4     NaN
    df_startenddate_exploded = df_startenddate.explode(column=int_loc).reset_index(drop=True)
    assert (
        len(int_loc_collector) != len(df_startenddate_exploded) == len(idmap_source_collector) == len(int_par_collector)
    )
    df_startenddate_exploded[idmap_source] = idmap_source_collector
    df_startenddate_exploded[int_par] = int_par_collector
    df_startenddate_exploded.drop_duplicates(keep="first", inplace=True)
    df_startenddate_exploded.reset_index(drop=True, inplace=False)
    # replace space/empty strings with NaN
    df_startenddate_exploded.replace(to_replace=r"^\s*$", value=np.nan, regex=True, inplace=True)
    new_columns = StartEndDateColumnChoices.get_all() + [
        ex_loc,
        ex_par,
        int_loc,
        int_par,
        idmap_source,
    ]
    df = df_startenddate_exploded[new_columns]
    return df
