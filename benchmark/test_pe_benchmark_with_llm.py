import pytest
import os

from benchmark.comm_llm import run_llm_benchmark

from .common import (
    ensure_target_result_directory_existed,
    prepare_dataset_for_benchmark,
)
from .constant import BASELINE, BenchmarkType, LLModelType


@pytest.mark.skip("just for test the feasible of claude api")
def test_claude(client):
    msg, useage = client.create(
        system_prompts="Respond only in Yoda-speak.",
        user_prompts="How are you today?",
    )

    print(msg)
    assert msg is not None


baseline = os.environ.get("BASELINE", BASELINE)
target = os.environ.get("TARGET", "2024-08-12")
baseline_dir = os.path.join("./benchmark/data/pe", baseline)
target_dir = os.path.join("./benchmark/data/pe", target)


@pytest.fixture(scope="module")
def prepared_dataset():
    return prepare_dataset_for_benchmark(
        baseline_dir=baseline_dir,
        target_dir=target_dir,
        benchmark_type=BenchmarkType.PE,
    )


@pytest.fixture(scope="module")
def ensured_result_path():
    result_dir = ensure_target_result_directory_existed(
        baseline=baseline,
        target=target,
        benchmark_type=BenchmarkType.PE,
    )
    return os.path.join(result_dir, "result.log")


def test_gpt4o_benchmark(client, prepared_dataset, ensured_result_path):
    run_llm_benchmark(
        dataset=prepared_dataset,
        benchmark_type=BenchmarkType.PE,
        model=LLModelType.GPT4O,
        result_file=ensured_result_path,
        client=client,
    )


def test_gemini15_benchmark(client, prepared_dataset, ensured_result_path):
    run_llm_benchmark(
        dataset=prepared_dataset,
        benchmark_type=BenchmarkType.PE,
        model=LLModelType.GEMINI15,
        result_file=ensured_result_path,
        client=client,
    )
