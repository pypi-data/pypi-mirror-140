import click
import datetime
from click.types import DateTime

from .base import AliasedGroup
from yucebio.yc2.adaptor.util.monitor import Monitor

@click.group('monitor', cls=AliasedGroup)
def cli():
    """作业监控"""
    pass


@cli.command()
@click.option('--page', '-p', help="分页页码", type=int, default=1, show_default=True)
@click.option('--page_size', '-ps', help="每页查询的数据量", type=int, default=50, show_default=True)
@click.option('--backend_name', '-b', help="按Cromwell配置过滤")
@click.option('--prefix', help="按prefix（分析任务编号）模糊查询")
@click.option('--sample_ids', '-sa', help="按样本编号模糊查询")
@click.option('--status', '-s', help="按作业状态查询", type=str)
@click.option('--detail', '-d', is_flag=True, default=False, help="显示详细信息（错误信息和当前运行中的步骤）", show_default=True)
def ls(**kw):
    """查看本人提交的任务最新状态
    
    固定展示以下列
    
    - Status： Ready/Waitdata(准备中，等待下机),Uploading(上传数据),Init(准备投递到Cromwell),Running,Finish,Aborted,Failed

    - Task_Count: 正在运行的任务数/运行中+已结束的任务数/总任务数

    - Workdir: 作业在Cromwell集群上的工作目录
    
    - Start/Duration：开始时间和分析时长（保留2位小数的小时）
    
    - Prefix/Project: Prefix/分析项目编号。若Project相同与Prefix相同，则简写为"-"
    
    - Samples：按照 tumor/normal/rna的顺序展示样本编号
    
    - WorkflowName: 流程名称
    
    - Metadata: Cromwell Metadata链接地址
    """
    monitor = Monitor(backend_name=kw['backend_name'])
    show_detail = kw.pop('detail')
    monitor.list_jobs(kw, show_detail=bool(show_detail))

@cli.command()
@click.option('--backend_name', '-b', help="cromwell server 配置名称", required=True)
@click.option('--id', '-j', help="cromwell 作业编号")
@click.option('--name', '-n', help="cromwell 流程名称")
@click.option('--status', '-s', help="cromwell 作业状态", type=click.Choice(['Submitted', 'Running', 'Aborting', 'Failed', 'Succeeded', 'Aborted']))
@click.option('--start', '-st', help="cromwell 开始时间", type=DateTime())
@click.option('--submission', '-su', help="cromwell 提交时间", type=DateTime())
@click.option('--page', '-p', help="分页页码", type=int)
@click.option('--pageSize', '-ps', help="每页查询的数据量", type=int)
@click.option('--save', help="是否保存到API服务器", is_flag=True, default=False)
def query(**kw):
    """基于Cromwell API接口查询所有任务基本信息

    参考: https://cromwell.readthedocs.io/en/stable/api/RESTAPI/#workflowqueryparameter
    """
    server = kw.pop('backend_name')
    params = {k:v for k,v in kw.items() if v and k != 'save'}
    for k in ['start', 'submission']:
        if not kw[k]:
            continue
        t: datetime.datetime = kw[k]
        params[k] = t.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    if not params:
        ctx = click.get_current_context()
        click.secho('请至少指定一种参数', fg='red')
        print(ctx.get_help())
        return

    monitor = Monitor(backend_name=server)
    data = monitor.query(params, server)

    total, results = data['totalResultsCount'], data['results']
    click.secho(f"总数据量：{total}", fg="green")

    save = kw['save']
    for job in results:
        try:
            cromwell_job = monitor.get(job['id'], server)
        except Exception as e:
            click.secho(f"{job['id']}\t{server}\t获取metadata失败：{e}")
            continue
        cromwell_job.format()

        if save:
            monitor.save(cromwell_job)


@cli.command()
@click.option('--show-command', '-s', is_flag=True, default=False, help="是否显示命令行内容", show_default=True)
@click.argument('prefix_or_cromwell_id')
def jobinfo(prefix_or_cromwell_id: str, show_command = False):
    """展示单个作业的执行详细信息，必须提供CromwellId或Prefix

    参考YC-Cloud1展示每个task的信息

    JobID	JobName	JobScript	JobState	Start	Stdout	Stderr	Command

    原理： 从cromwell获取metadata信息，解析其中的calls
    """
    monitor = Monitor()
    metadata = monitor.api.get_metadata(prefix_or_cromwell_id)
    click.secho(f"Cromwell Metadata: {monitor.api.api}/api/v1/workflow/{metadata.get('id', '-')}/metadata", fg='green')
    calls = metadata.get('calls', {})
    header = ["JobID", "JobName", "JobState", "Start", "End", "Stdout", "Stderr", "Command"]
    print("\t".join(header))

    for taskname, items in calls.items():
        # jobId, executionStatus, shardIndex, 
        for idx, taskitem in enumerate(items):
            job = [
                ("jobId", taskitem.get('jobId', '-')),
                ("name", f"{taskname}.{idx}"),
                ("status", taskitem.get('executionStatus', '-')),
                ("start", taskitem.get('start', '-')),
                ("end", taskitem.get('end', '-')),
                ("stdout", taskitem.get('stdout', '-')),
                ("stderr", taskitem.get('stderr', '-')),
                ["command", taskitem.get('commandLine', '-')],
            ]
            if not show_command:
                job[-1][1] = '-'
            line = [i[1] for i in job]
            print("\t".join(line))

