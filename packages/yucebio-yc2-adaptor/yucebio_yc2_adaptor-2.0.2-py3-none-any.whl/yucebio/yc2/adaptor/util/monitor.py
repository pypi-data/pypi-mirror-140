"""获取作业状态
"""
import dateutil.parser
import re
import sys
from typing import OrderedDict
import requests
from yucebio.yc2.adaptor.util.config import Config
import click
from . import types

config = Config(check_user=False)

class Monitor:

    def __init__(self, backend_name: str = None, check_user=True) -> None:
        if check_user:
            config.check_user()
        self.api = config.api
        self.backend_config : types.CromwellBackendType = None
        if backend_name:
            self.init_backend_config(backend_name)

    def init_backend_config(self, backend_alias: str):
        """在预设和自定义backend中找到最匹配的
        """
        if self.backend_config and self.backend_config["alias"] == backend_alias:
            return
        self.backend_config = config.get_backend_config(backend_alias)

    @property
    def owner(self):
        return config.get('owner', '')

    def get(self, jobid: str, server_alias: str, auto_update: bool = True):
        """从cromwell api中获取作业最新状态

        Args:
            jobid (str): cromwell 作业id
            server_alias (str): cromwell server地址
            auto_update (bool): 检测到任务完成时，是否自动更新到数据库
        """
        cromwell_job = CromwellJob(jobid, host=self.backend_config["host"])
        cromwell_job.get_metadata()
        return cromwell_job

    def query(self, params: dict, backend_name: str):
        """基于Cromwell API接口查询数据，Refer to https://cromwell.readthedocs.io/en/stable/api/RESTAPI/#workflowqueryparameter
        """
        # api = config.get_cromwell_backend(backend_name)["host"]
        api = self.backend_config["host"]
        url = f"{api}/api/workflows/v1/query"
        try:
            rsp = requests.get(url, params=params)
            if not rsp.ok:
                print(url, params)
                raise RuntimeError(rsp.reason)
            return rsp.json()
        except Exception as e:
            raise e

    def list_jobs(self, params: dict={}, show_detail: bool = False):
        """查看本人所有任务
        """
        page = params.get('page', 1)
        pageSize = params.get('page_size', 10)
        skip = (page - 1) * pageSize
        if skip <= 0:
            skip = 0

        api_params = {k:v for k,v in params.items() if k not in ['page', 'page_size', 'backend_name']}
        api_params['owner'] = self.owner
        if params.get('backend_name'):
            self.init_backend_config(params['backend_name'])
            backend = self.backend_config.get('platform', self.backend_config.get('backend'))

            api_params['backend.backend'] = backend

        workflows, totals = self.api.get_workflows(api_params, paginations={"offset": skip, "limit": pageSize})
        if not workflows:
            return

        click.secho(f"第{skip}-{skip + len(workflows)}条，总共 {totals} 条数据", fg="green")

        # 打印表头
        format = '{status:10s}\t{count}\t{workflow_name}\t{duration}\t{sample_ids}\t{prefix}\t{workdir}\t{url}'
        header = {
            "status": "Status",                   # Succeeded
            "count": "TaskCount",
            "prefix": "Prefix/Project",    # 20211116.ClinicRapid.2103062.MT1011.104406
            "sample_ids": "Samples",           # DN2003922SLZDA26
            "workflow_name": "WorkflowName",
            "workdir": "Workdir",
            "duration": "Start/Duration",
            "url": "Metadata",
        }
        print(format.format(**header))
        patt_datetime = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z')
        for workflow in workflows:
            # self.format_api_workflow(workflow, show_detail=show_detail)
            row = {k: workflow.get(k, '-') for k in header}
            if workflow.get('cromwell_id'):
                backend_host = workflow["backend"]["host"]
                row['url'] = f"{backend_host}/api/workflows/v1/{workflow['cromwell_id']}/metadata"
            project = workflow.get('project', 'NA')
            if project == workflow.get('prefix', 'NA'):
                project = '-'
            row['prefix'] = f"{row['prefix']}/{project}"
            # 计算分析时长
            start, end = '', ''
            if workflow.get('start') and patt_datetime.match(workflow['start']):
                start = dateutil.parser.isoparse(workflow['start'])
            if workflow.get('end') and patt_datetime.match(workflow['end']):
                end = dateutil.parser.isoparse(workflow['end'])
            if start and end:
                duration = (end - start).seconds/3600
                start = start.strftime('%Y-%m-%dT%H:%M:%S')
                row['duration'] = f"{start}/{duration:.2f}h"
            # 计算任务数目
            count_running = len(workflow.get('running_tasks', []))
            count_done = len(workflow.get('calls', []))
            count_total = workflow.get('wdl', {}).get("task_count", "-")
            row['count'] = f"{count_running}/{count_done}/{count_total}"

            print(format.format(**row))

            if workflow["status"] == 'Running' and show_detail:
                for running_task in workflow.get("running_tasks", []):
                    print(click.style(f"RUNNING:\t{running_task}", fg="yellow"))

            if show_detail:
                for r in workflow.get("failures", []):
                    print(click.style(f"FAIL_REASON:\t{r}", fg="red"), file=sys.stderr)

    def format_api_workflow(self, workflow: types.WorkflowType, show_detail: bool = False):
        backend_host = workflow["backend"]["host"]
        url = "-"
        if workflow.get('cromwell_id'):
            url = f"{backend_host}/api/workflows/v1/{workflow['cromwell_id']}/metadata"
        msg = f'{workflow["status"]:10s}\t{workflow.get("prefix", "-"):40s}\t{workflow.get("sample_ids", "-"):32s}\t{workflow.get("workflow_name", "-"):15s}\t\t {url}\t{workflow.get("workdir", "-")}'
        duration = f"\t{workflow.get('start', '-')}:{workflow.get('end', '-')}"
        msg += duration


        if workflow["status"] == 'Running' and show_detail:
            for running_task in workflow.get("running_tasks", []):
                msg += click.style(f"\nRUNNING:\t{running_task}", fg="yellow")
        print(msg)

        if show_detail:
            for r in workflow.get("failures", []):
                print(click.style(f"\nFAIL_REASON:\t{r}", fg="red"), file=sys.stderr)

class CromwellJob:
    def __init__(self, cromwell_id: str, host: str=None) -> None:
        self.cromwell_id = cromwell_id
        self.api = host
        self.metadata = {}
        self.call_details = []

        # 需要从inputs中提取的额外内容
        self.owner = ""
        self.prefix = ""
        self.samples = ""

    def get_metadata(self):
        """从cromwell api中获取作业最新状态
        """
        if self.metadata:
            return

        url = f"{self.api}/api/workflows/v1/{self.cromwell_id}/metadata"
        rsp = requests.get(url)
        if not rsp.ok:
            raise RuntimeError(f"{url}\t{rsp.reason}")

        metadata: dict = rsp.json()
        self.parse_metadata(metadata)

    def parse_metadata(self, metadata: dict):
        """解析metadata数据
        """
        self.metadata = metadata
        if not self.metadata:
            return
        self.status = self.metadata.get('status')
        for k in ["workflowName", "id", "status", "submission", "start", "end"]:
            self.__dict__[k] = self.metadata.get(k, "")

        # 解析calls
        calls = self.metadata.get('calls')
        if isinstance(calls, dict):
            for task_name, task_items in calls.items():
                idx = -1
                for task_item in task_items:
                    idx += 1
                    info = {
                        k: task_item.get(k, '-') for k in [
                            "executionStatus", "jobId", "backend", "start", "end", "callRoot",
                        ]
                    }
                    failures = task_item.get('failures')
                    if failures:
                        failures = self.parse_failures(failures)
                    self.call_details.append((task_name, idx, info, failures))

        self.parse_inputs()

    def parse_inputs(self):
        """解析inputs，提取一些必要信息"""
        inputs = self.metadata.get('inputs', {})
        if inputs:
            self.prefix = inputs.get('prefix', 'NA')

            tumor_id = inputs.get('tumor_id', None)
            normal_id = inputs.get('normal_id', None)
            rna_id = inputs.get('rna_id', None)
            sample = "-VS-".join([v for v in [tumor_id, normal_id] if v])
            sample = ",".join([v for v in [sample, rna_id] if v])
            self.samples = sample

            self.owner = inputs.get('owner', "")

    def parse_failures(self, failures: list):
        reasons = []
        for failure in failures:
            casedBy = failure.get('causedBy')
            if casedBy:
                reasons += self.parse_failures(failure['causedBy'])
            else:
                if failure.get('message'):
                    reasons.append(failure['message'])

        return reasons

    def format(self):
        key_lables = OrderedDict([
            ("workflowName", "流程名称"),
            ("id", "Workflow Id"),
            ("status", "状态"),
            ("submission", "提交时间"),
            ("start", "开始时间"),
            ("end", "结束时间"),
            # ("prefix", "分析项目号"),
            # ("samples", "样本")
        ])
        basic_infos = {k: self.metadata.get(k, "-") for k in key_lables}


        url = f"{self.api}/api/workflows/v1/{self.cromwell_id}/metadata"
        basic_infos["id"] = url
        msg = f"{basic_infos['status']}\t{self.prefix:15s}\t{self.samples:20s}\t{basic_infos['workflowName']:15s}\t{url}\t{basic_infos['submission']}"

        if self.status == 'Running':
            for running_task in self.current_running_tasks():
                msg += click.style(f"\nRUNNING:\t{running_task}", fg="yellow")
        print(msg)

        for r in self.fail_reason():
            print(click.style(f"\nFAIL_REASON:\t{r}", fg="red"), file=sys.stderr)

    def current_running_tasks(self):
        tasks = []
        for call in self.call_details:
            task_name, idx, info, failures = call
            if info.get('executionStatus') == 'Running':
                tasks.append(f"{task_name}[{idx}]\t{info['jobId']}\t{info['start']}")
            
        return tasks

    def fail_reason(self):
        if not self.call_details:
            # 直接从顶级的failures中提取错误信息
            return self.parse_failures(self.metadata.get('failures', []))
        reasons = []
        for call in self.call_details:
            task_name, idx, info, failures = call
            if not failures:
                continue
            reasons += [f"{task_name}[{idx}]\t{f}" for f in failures]
        return reasons