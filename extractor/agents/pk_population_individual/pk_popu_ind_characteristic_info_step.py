from extractor.agents.pk_population_individual.pk_popu_ind_common_step import PKPopuIndCommonAgentStep
from extractor.agents.pk_population_individual.pk_popu_ind_common_agent import (
    PKPopuIndCommonAgentResult,
)
from extractor.agents.pk_population_individual.pk_popu_ind_characteristic_info_agent import (
    CHARACTERISTIC_INFO_PROMPT,
    CharacteristicInfoResult,
    post_process_characteristic_info,
)
from extractor.agents.pk_population_individual.pk_popu_ind_workflow_utils import PKPopuIndWorkflowState


class CharacteristicInfoExtractionStep(PKPopuIndCommonAgentStep):
    def __init__(self):
        super().__init__()
        self.start_title = "Extracting Characteristic Information"
        self.end_title = "Completed to Extract Characteristic Information"

    def get_system_prompt(self, state):
        title = state["title"]
        full_text = state["full_text"]
        return CHARACTERISTIC_INFO_PROMPT.format(
            title=title,
            full_text=full_text,
        )

    def leave_step(
        self,
        state: PKPopuIndWorkflowState,
        res: PKPopuIndCommonAgentResult,
        processed_res=None,
        token_usage=None,
    ):
        if processed_res is not None:
            state["md_table_characteristic"] = processed_res
            self._step_output(state, step_output="Result (md_table_characteristic):")
            self._step_output(state, step_output=processed_res)
        super().leave_step(state, res, processed_res, token_usage)

    def get_schema(self):
        return CharacteristicInfoResult

    def get_post_processor_and_kwargs(self, state):
        return post_process_characteristic_info, None
