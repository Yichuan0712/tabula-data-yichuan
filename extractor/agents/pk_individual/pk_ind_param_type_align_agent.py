from langchain_core.prompts import ChatPromptTemplate
from pydantic import Field

from TabFuncFlow.utils.table_utils import (
    fix_col_name,
    markdown_to_dataframe,
    dataframe_to_markdown,
)
from TabFuncFlow.operations.f_transpose import f_transpose
from TabFuncFlow.utils.table_utils import (
    deduplicate_headers,
    fill_empty_headers,
    remove_empty_col_row,
)
from extractor.agents.pk_individual.pk_ind_common_agent import PKIndCommonAgentResult

PARAMETER_TYPE_ALIGN_PROMPT = ChatPromptTemplate.from_template("""
There is now a table related to pharmacokinetics (PK). 
{md_table_individual}
The extracted table headers are as follows:
{md_table_individual_header}
Carefully examine the pharmacokinetics (PK) table and follow these steps to determine how the PK parameter type is represented:
(1) Identify how the PK parameter type (e.g., Cmax, tmax, t1/2, etc.) is structured in the table:
Please answer in the following format:
col_name: column name, it represents the PK parameter type serves as the row header or is listed under the specific column. If the PK parameter type is represented as column headers, return None.
(2) Ensure a thorough analysis of the table structure before selecting your answer.
""")


class ParameterTypeAlignResult(PKIndCommonAgentResult):
    col_name: str | None = Field(
        description="""The name of the column representing the PK parameter type, which serves as the row header or is listed under a specific column. 
If the PK parameter type is represented as column headers, this value will be None."""
    )

def get_parameter_type_align_prompt(md_table_individual: str):
    df = markdown_to_dataframe(md_table_individual)
    headers = [f'"{col}"' for col in df.columns]
    headers = ",".join(headers)
    return PARAMETER_TYPE_ALIGN_PROMPT.format(
        md_table_individual=md_table_individual,
        md_table_individual_header=headers,
    )

def post_process_parameter_type_align(
    res: ParameterTypeAlignResult, md_table_individual: str
):
    """Please note: the condition for transposing is the opposite of that for PK summary"""
    df_table = markdown_to_dataframe(md_table_individual)
    # if res.col_name is None:
    #     df_table = f_transpose(df_table)
    #     df_table.columns = ["Parameter type"] + list(df_table.columns[1:])
    #     return deduplicate_headers(
    #         fill_empty_headers(remove_empty_col_row(dataframe_to_markdown(df_table)))
    #     )
    # else:
    #     col_name = fix_col_name(res.col_name, md_table_individual)
    #     df_table = df_table.rename(columns={f"{col_name}": "Parameter type"})
    #     return dataframe_to_markdown(df_table)
    if res.col_name is None:
        # col_name = fix_col_name(res.col_name, md_table_individual)
        # df_table = df_table.rename(columns={f"{col_name}": "Parameter type"})
        return dataframe_to_markdown(df_table)
    else:
        df_table = f_transpose(df_table)
        # df_table.columns = ["Parameter type"] + list(df_table.columns[1:])
        return deduplicate_headers(
            fill_empty_headers(fill_empty_headers(remove_empty_col_row(dataframe_to_markdown(df_table))))
        )
