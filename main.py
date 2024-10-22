import asyncio
import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Sequence
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio import activity, workflow
from temporalio.common import RawValue
import funcs


@dataclass
class CustomDataclass:
    fn: str
    args: Sequence


@activity.defn(dynamic=True)
async def dynamic_activity(args: Sequence[RawValue]):
    arg = activity.payload_converter().from_payload(args[0].payload, CustomDataclass)
    fn = getattr(funcs, arg.fn)
    return await fn(arg.args)


@workflow.defn(dynamic=True)
class DynamicWorkflow:
    @workflow.run
    async def run(self, args: Sequence[RawValue]):
        arg = workflow.payload_converter().from_payload(args[0].payload, CustomDataclass)
        return await workflow.execute_activity(
            arg.fn,
            arg,
            start_to_close_timeout=timedelta(seconds=10),
        )


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="dynamic-task-queue",
        workflows=[DynamicWorkflow],
        activities=[dynamic_activity],
    ):

        result = await client.execute_workflow(
            "YourWorkflowName",
            arg=CustomDataclass(fn="multiply", args=[3, 4]),
            task_queue="dynamic-task-queue",
            id=str(uuid.uuid4()),
        )
        print(f"Workflow completed with result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
