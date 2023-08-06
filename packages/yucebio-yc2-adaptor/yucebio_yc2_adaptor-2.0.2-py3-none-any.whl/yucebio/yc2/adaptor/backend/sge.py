import click, sys
from .base import BaseAdaptor
from yucebio.yc2.adaptor.util.wdl_processor import _TaskItem, _WorkflowCallItem


class Adaptor(BaseAdaptor):
    """转换WORKFLOW到泰州SGE平台

    不需要额外处理，Cromwell的SGE backend中可以支持singularity适配
    """
    PLATFORM = "SGE"
    SUPPORTED_RUNTIME_ATTRIBUTES = ['cpu', "mem", 'memory', 'maxRetries', "sge_queue", "sge_project", "simg", "mount", 'continueOnReturnCode', 'owner']

    def convert(self):
        # 遍历calls初始化被调用task对应关系
        call_tasks = self.workflow_processor.call_tasks

        # 1. 遍历每个import
        for ns, import_item in self.workflow_processor.imports.items():
            if ns not in call_tasks:
                raise RuntimeError(f"Line #{import_item.line} 请移除未使用的导入内容 {import_item.path}")
            call_task_info = call_tasks[ns]

            # 2. 依次检测每个子任务，跳过无关的task
            task_processor = import_item.wdl
            click.secho(f"\n########## Process WDL [{task_processor.fileWdl}] ...", fg='yellow', file=sys.stderr)
            for wdl_task_item in task_processor.meta_tasks:
                task_name = wdl_task_item.name
                if task_name not in call_task_info:
                    print(f"########## Task [{wdl_task_item.name}] 未参与本次分析，准备移除...", file=sys.stderr)
                    wdl_task_item.delete_content()
                    continue

                print(f"########## Process Task [{task_name}] ", file=sys.stderr)
                # SGE 平台只需要过滤掉不支持的RUNTIME属性
                self.filter_or_append_runtime_attributes(wdl_task_item)

                # 将runtime中的 memory 转换成字符串
                runtime_mem = wdl_task_item.runtime.get('memory')
                if not runtime_mem:
                    continue

                # 3.1 runtime.memory是固定值，直接转换
                if runtime_mem not in wdl_task_item.inputs:
                    wdl_task_item.update_runtime("memory", f'"{runtime_mem} GB"')
                    continue
                # 3.2. runtime.memory是变量
                else:
                    wdl_task_item.update_runtime("memory", '"~{' + runtime_mem  +'} GB"')
