from abc import ABC, abstractmethod
from typing import Any, Callable, Optional
import logging

from extractor.agents.pk_individual.pk_ind_workflow_utils import PKIndWorkflowState
from extractor.agents.agent_prompt_utils import INSTRUCTION_PROMPT
from extractor.agents.pk_individual.pk_ind_workflow_utils import (
    pk_ind_enter_step,
    pk_ind_leave_step,
)
from extractor.agents.pk_individual.pk_ind_common_agent import (
    PKIndCommonAgentResult,
    PKIndCommonAgent,
)

logger = logging.getLogger(__name__)


class PKIndCommonStep(ABC):
    def __init__(self):
        super().__init__()
        self.start_title = ""
        self.start_descp = ""
        self.end_title = ""

    def enter_step(self, state: PKIndWorkflowState):
        pk_ind_enter_step(state, self.start_title, self.start_descp)

    def leave_step(
        self,
        state: PKIndWorkflowState,
        res: PKIndCommonAgentResult | None = None,
        processed_res: Any | None = None,
        token_usage: dict | None = None,
    ):
        pk_ind_leave_step(
            state=state,
            step_output=self.end_title,
            step_reasoning_process=res["reasoning_process"]
            if res is not None and "reasoning_process" in res
            else None,
            token_usage=token_usage,
        )

    def _step_output(
        self,
        state: PKIndWorkflowState,
        step_output: Optional[str] = None,
        step_reasoning_process: Optional[str] = None,
    ):
        def default_output(
            step_output: Optional[str] = None,
            step_reasoning_process: Optional[str] = None,
        ):
            if step_reasoning_process is not None:
                logger.info(f"\n\nReasoning: \n{step_reasoning_process}\n\n")
            if step_output is not None:
                logger.info(step_output)

        step_callback = (
            state["step_callback"]
            if "step_callback" in state and state["step_callback"] is not None
            else default_output
        )
        step_callback(
            step_reasoning_process=step_reasoning_process,
            step_output=step_output,
        )

    def execute(self, state: PKIndWorkflowState):
        self.enter_step(state)
        res, processed_res, token_usage = self.execute_directly(state)
        self.leave_step(state, res, processed_res, token_usage)

        return state

    @abstractmethod
    def execute_directly(
        self,
        state: PKIndWorkflowState,
    ) -> tuple[PKIndCommonAgentResult, Any | None, dict | None]:
        """execute directly"""


class PKIndCommonAgentStep(PKIndCommonStep):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_system_prompt(self, state: PKIndWorkflowState):
        """get system prompt"""

    def get_instruction_prompt(self, state: PKIndWorkflowState):
        """get instruction prompt"""
        return INSTRUCTION_PROMPT

    @abstractmethod
    def get_schema(self) -> PKIndCommonAgentResult | dict:
        """get result schema (pydantic BaseModel or json schema)"""

    @abstractmethod
    def get_post_processor_and_kwargs(
        self, state: PKIndWorkflowState
    ) -> tuple[
        Callable | None,
        dict | None,
    ]:
        """get post_processor and its kwargs"""

    def execute_directly(
        self, state: PKIndWorkflowState
    ) -> tuple[
        PKIndCommonAgentResult,
        Any | None,
        dict | None,
    ]:
        """execute step directly"""
        system_prompt = self.get_system_prompt(state)
        instruction_prompt = self.get_instruction_prompt(state)
        llm = state["llm"]
        schema = self.get_schema()
        post_process, kwargs = self.get_post_processor_and_kwargs(state)
        agent = PKIndCommonAgent(llm=llm)
        if kwargs is not None:
            res, processed_res, token_usage = agent.go(
                system_prompt=system_prompt,
                instruction_prompt=instruction_prompt,
                schema=schema,
                post_process=post_process,
                **kwargs,
            )
        else:
            res, processed_res, token_usage = agent.go(
                system_prompt=system_prompt,
                instruction_prompt=instruction_prompt,
                schema=schema,
                post_process=post_process,
            )
        reasoning_process = ""
        if res is not None:
            try:
                reasoning_process = (
                    res["reasoning_process"]
                    if type(res) == dict
                    else res.reasoning_process
                )
            except Exception as e:
                logger.error(
                    f"Failed to access res.reasoning_process.\nError is {str(e)}"
                )
                pass
        self._step_output(state, step_reasoning_process=reasoning_process)
        return res, processed_res, token_usage
