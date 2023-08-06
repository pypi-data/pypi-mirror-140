# -*- coding: utf-8 -*-
"""Query PDB for structures."""
# standard library imports
import datetime
import json
import operator
import time
from functools import reduce
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import pandas as pd
from Bio.Seq import Seq  # type: ignore
from Bio import SeqIO  # type: ignore
from Bio.SeqRecord import SeqRecord  # type: ignore
from dotli import Dotli  # type: ignore
from gql import Client
from gql import gql
from gql.transport.aiohttp import AIOHTTPTransport
from loguru import logger
from rcsbsearch import Attr as RCSBAttr  # type: ignore
from rcsbsearch import rcsb_attributes as rcsbsearch_attributes  # type: ignore
from rcsbsearch.search import Terminal  # type: ignore
from statsdict import Stat

from . import rcsb_attributes
from .common import APP
from .common import NAME
from .common import RCSB_DATA_GRAPHQL_URL
from .common import STATS
from .config import read_config

OPERATOR_DICT = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt,
}
RESOLUTION_FIELD = "rcsb_entry_info.diffrn_resolution_high.value"
ID_FIELD = "rcsb_id"
ID_FIELD_LEN = 4
RESOLUTION_FIELD = "rcsb_entry_info.diffrn_resolution_high.value"
RESOLUTION_LABEL = "resolution, Å"
SEQ_FIELD = "polymer_entities.entity_poly.pdbx_seq_one_letter_code_can"
FIXED_METADATA = [
    {"field": ID_FIELD, "type": "str", "name": "rcsb_id"},
    {"field": RESOLUTION_FIELD, "type": "float", "name": RESOLUTION_LABEL},
    {"field": SEQ_FIELD, "type": "seq", "name": "seq"}
]
METADATA_TIMEOUT = 120
CONFIG = read_config(NAME)

@APP.command()
def rcsb_attributes_to_py() -> None:
    """Write RCSB attributes list as python code."""
    outfile = "rcsb_attributes.py"
    logger.info(f'Writing RCSB attributes list to "{outfile}".')
    with Path(outfile).open("w") as fp:
        date = datetime.date.today()
        fp.write(f'"""Set of RCSB attributes as of {date}."""\n')
        fp.write("rcsb_attr_set = (\n")
        for attrib in rcsbsearch_attributes:
            fp.write(f'    "{attrib.attribute}",\n')
        fp.write(")\n")


def rcsb_search_query(
    field: str, op_str: str, val: Union[int, float, str]
) -> Terminal:
    """Convert query specifiers to queries."""
    if field not in rcsb_attributes.rcsb_attr_set:
        raise ValueError(f'Unrecognized RCSB field "{field}"')
    try:
        op = OPERATOR_DICT[op_str]
    except KeyError:
        raise ValueError(
            f'Unrecognized RCSB operator string "{op_str}"'
        ) from None
    return op(RCSBAttr(field), val)


def construct_rcsb_data_query(id_list: List[str], fields: List[str]) -> str:
    """Construct an RCSB GraphQL data query JSON object.

    We use the flattened field names from rcsbsearch in
    dot-separated form for input because they are much
    easier to specify and check.
    """
    for field in fields:
        if field not in rcsb_attributes.rcsb_attr_set:
            raise ValueError(
                f'Unrecognized RCSB attribute "{field}"'
            ) from None
    unflattener = Dotli().unflatten
    fixed_query_dict = unflattener(dict.fromkeys(fields, 0))
    fixed_query_str = json.dumps(fixed_query_dict, indent=1)
    query_set = (
        fixed_query_str.replace(": 0", "")
        .replace(":", "")
        .replace('"', "")
        .replace(",", "")
    )
    id_list_str = json.dumps(id_list)
    query_str = f"""query {{
  entries(entry_ids: {id_list_str})
  {query_set}
}}"""
    return query_str

def delist_single_lists(uglyiter: Dict[str, Any]) -> Dict[str, Any]:
    """Change single-item lists into the items they contain."""
    cleaned = uglyiter.copy()
    for k, v in cleaned.items():
        if isinstance(v, list) and len(v) == 1:
            singleitem = v[0]
            if isinstance(singleitem, dict):
                cleaned[k] = delist_single_lists(singleitem)
            else:
                cleaned[k] = singleitem
    return cleaned


@APP.command()
def rcsb_metadata(
    id_list: List[str], show_frame: Optional[bool] = False
) -> Tuple[pd.DataFrame, List[Any]]:
    """Query the RCSB GraphQL endpoint for metadata.

    Example:
        rcsb_metadata 1STP 2JEF
    """
    myconfig = CONFIG.metadata
    # Do asynchronous I/O to RCSB.
    transport = AIOHTTPTransport(url=RCSB_DATA_GRAPHQL_URL)
    # Create a GraphQL client.
    client = Client(transport=transport,
                    fetch_schema_from_transport=True,
                    execute_timeout=METADATA_TIMEOUT)
    # Construct the query from a query string.
    metadata_list = FIXED_METADATA + myconfig.extras
    query_fields = [f["field"] for f in metadata_list]
    query_str = construct_rcsb_data_query(id_list, query_fields)
    logger.debug(f"GraphQL query={query_str}")
    query = gql(query_str)
    # Execute the query.
    results = client.execute(query)["entries"]
    logger.debug(f"raw query results={results}")
    if myconfig.unpack_lists:
        # RCSB's GraphQL returns a rather complex object
        # with lists consisting of one dictionary in many cases.
        # If "unpack_lists" is set, these one-dict lists will
        # be converted to dicts.  Without this, you will get
        # a bunch of fields including ".0." upon flattening
        # which will get deleted later by default.
        results = [delist_single_lists(e) for e in results]
        logger.debug(f"after fixing lists, results = {results}")
    flattener = Dotli().flatten
    results = [flattener(e) for e in results]
    if myconfig.delete_unknown_fields:
        # If a query field returns "none" and it is
        # the only field in that query category,
        # the parent field will get returned by
        # itself.  Deleting all unknown fields
        # prevents putting parents in the output
        # table.
        for pos, entry in enumerate(results):
            unfulfilled = []
            for k in entry.keys():
                if k not in query_fields:
                    logger.debug(
                        f"deleting unfulfilled key {k} in {entry[ID_FIELD]}"
                    )
                    unfulfilled.append(k)
            for item in unfulfilled:
                del results[pos][item]
    # Now create a data frame from the list of result dictionaries.
    df = pd.DataFrame.from_dict(results)
    df = df.set_index(ID_FIELD)
    df = df.rename(columns={f["field"]: f["name"] for f in metadata_list})
    seq_list = []
    has_seq = []
    for id, seq  in df["seq"].iteritems():
        if pd.isnull(seq):
            logger.warning(f"entry {id} has no sequence record")
            has_seq.append(False)
        else:
            seq_list.append(SeqRecord(Seq(seq), id))
            has_seq.append(True)
    del df["seq"]
    df["has_seq"] = has_seq
    if myconfig.delete_unknown_fields:
        # order output columns in order in extras
        col_order = [
            f["name"] for f in metadata_list if f["name"] in df.columns
        ]
        df = df[col_order]
    if show_frame:
        print(df)
    return df, seq_list


@APP.command()
@STATS.auto_save_and_report
def query(
    set_name: str,
    neutron_only: Optional[bool] = False,
    query_only: Optional[bool] = False,
) -> None:
    """Query PDB for structures as defined in config file."""
    myconfig = CONFIG.query
    extra_queries = [rcsb_search_query(**e) for e in myconfig.extras]
    if neutron_only:
        subtypes = ["neutron"]
    else:
        subtypes = myconfig.subtypes
    all_keys = []
    all_types = []
    metadata_frames = []
    for subtype in subtypes:
        resolution = myconfig[subtype].resolution
        label = myconfig[subtype].label
        STATS[f"{label}_resolution"] = Stat(
            resolution, units="Å", desc="Minimum resolution"
        )
        query_list = (
            [rcsb_search_query(RESOLUTION_FIELD, "<=", resolution)]
            + [rcsb_search_query(**e) for e in myconfig[subtype].extras]
            + extra_queries
        )
        combined_query = reduce(operator.iand, query_list)
        start_time = time.time()
        results = list(combined_query().iquery())
        n_results = len(results)
        if not query_only:
            category_frame, seqs = rcsb_metadata(results)
            category_frame["category"] = label
            metadata_frames.append(category_frame)
        elapsed_time = round(time.time() - start_time, 1)
        logger.info(
            f"RCSB returned {n_results} {label} structures <= {resolution} Å"
            + f" in {elapsed_time} s."
        )
        STATS[f"{label}_structures"] = Stat(
            n_results, desc=f"{label} structures in PDB"
        )
        all_keys += results
        all_types += [subtype] * n_results
    STATS["total_structures"] = Stat(len(all_keys), desc="Total structures")
    if not query_only:
        df = pd.concat(metadata_frames)
        df.sort_values(by=RESOLUTION_LABEL, inplace=True)
        STATS["metadata_cols"] = Stat(
            len(df.columns), desc="# of metadata fields"
        )
        df.to_csv(set_name + ".tsv", sep="\t")
        STATS["missing_seqs"] = Stat(
            len(df) - len(seqs), desc="# of RCSB entries w/o sequence"
        )
        SeqIO.write(seqs, set_name + ".fa", "fasta")
