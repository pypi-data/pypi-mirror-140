import sys
import click
from .base import AliasedGroup, show_error
from yucebio.yc2.adaptor.util.config import Config


@click.group('api', cls=AliasedGroup)
def cli():
    """通过适配器服务的形式管理Cromwell作业、Backend等
    """
    pass

@cli.command()
# @click.option('--backend_name', '-b', help="Cromwell backend别名")
@click.option('--cromwell_id', '-j', help = "Cromwell作业编号")
@click.option('--prefix', '-p', help = "自定义分析任务编号")
@click.option('--file_type', '-t', help="指定导出类型，支持json, wdl, files, standard_data", default="json")
def export_workflow(cromwell_id, prefix, file_type):
    """导出已有作业的原始内容，如input.json

    导出类型：

        1. json: 导出Cromwell最终使用的JSON数据。

        2. wdl: 导出Cromwell最终使用的流程定义内容

        3. files: 创建一个下载分析中间结果的后台作业。

        4. standard_data: 导出投递任务时使用的"标准数据格式"。
    """
    if prefix and cromwell_id:
        return show_error("只能使用一种编号")

    if not prefix and not cromwell_id:
        return show_error("至少指定一种编号")

    do_action('export_workflow', {"type": file_type}, primary_value=cromwell_id if cromwell_id else prefix)


@cli.command()
@click.option('--backend_name', '-b', help="Cromwell backend别名")
@click.argument('cromwell_ids', nargs=-1)
def link_job(backend_name, cromwell_ids):
    """关联一个已存在的作业
    
    CROMWELL_IDS: 一个或多个待关联的Crowmell作业编号
    """
    api = Config().api
    for cromwell_id in cromwell_ids:
        try:
            msg = api.submit_action('link', {"cromwell_id": cromwell_id, "backend_name": backend_name})
        except Exception as e:
            click.secho(f"关联失败：{cromwell_id} {e}", fg='red', file=sys.stderr)
        else:
            click.secho(f"关联成功: {cromwell_id} {msg}", fg="green")

def do_action(action: str, data: dict, primary_value: str = 'action', expect_response_type: str='json'):
    """基于Restful接口执行自定义操作

    当primary_value=='action'时，表示操作的是整个资源
    """
    c = Config()
    api = c.api
    try:
        msg = api.submit_action(action, data, primary_value=primary_value, expect_response_type=expect_response_type)
        if expect_response_type != 'json':
            return msg
    except Exception as e:
        click.secho(f"操作失败：{e}", fg='red', file=sys.stderr)
    else:
        click.secho(f"操作成功: {msg}", fg="green")

@cli.command()
@click.option('--backend_name', '-b', help="按别名过滤", type=str, default=None)
def list_backends(backend_name):
    """获取服务器支持的所有Cromwell Backend

    按照 host backend owner alias 列出所有已存在的cromwell backends。
    """
    print("\t".join(["HOST", "Backend", "Owner", "Alias"]))
    api = Config().api
    backends = api.get_backends(backend_name)
    for backend in backends:
        print("\t".join([backend.get(k, '-') for k in ['host', 'backend', 'owner', 'alias']]))


@cli.command()
@click.argument('json', nargs=-1)
def submit(**kw):
    """通过“标准数据格式”创建通用流程(适用于生产人员，由YC2自动完成数据上传工作)

    JSON: 适用于V2版本的JSON文件。其中包含模板、样本、分析流程、动态监控基本信息。后台会自动上传数据

    参考：http://gitlab.yucebio.com/python-packages/wdl_api/tree/bug/workflow#%E6%8E%A5%E5%8F%A3-version-2
    """
    api = Config().api
    for jsonfile in kw["json"]:
        try:
            msg = api.submit_by_standrand_data(jsonfile)
        except Exception as e:
            click.secho(f"任务信息上传失败：{e}，请手动将作业信息上传到服务器或联系开发人员", fg='red', file=sys.stderr)
        else:
            click.secho(f"上传成功: {msg}", fg="green")
