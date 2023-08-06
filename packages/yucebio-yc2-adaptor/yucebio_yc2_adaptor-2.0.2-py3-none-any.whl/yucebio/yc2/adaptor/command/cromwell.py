import imp
import sys
import click
from .base import AliasedGroup
# from yucebio_wdladaptor.util.config import Config
# from yucebio_wdladaptor.backend import SUPPORTTED_BACKENDS, PLACEHOLDER_SIMG_PATH, PLACEHOLDER_GLOBAL_PATH, BaseAdaptor
from yucebio.yc2.adaptor.util.api import WDLAPI
from yucebio.yc2.adaptor.util.config import Config
from yucebio.yc2.adaptor.backend import SUPPORTTED_BACKENDS, PLACEHOLDER_GLOBAL_PATH, PLACEHOLDER_SIMG_PATH


@click.group('config', cls=AliasedGroup)
def cli():
    """查看或管理Cromwell Backend配置"""
    pass


@cli.command()
@click.option("--backend", "-b", type=click.Choice(list(SUPPORTTED_BACKENDS)), required=True, help="platform")
@click.option("--alias", "-a", help="Cromwell Backend别名", default=None)
@click.option('--host', '-h', help="Cromwell Backend 的 Host 地址", required=True)
@click.option('--global_path', '-g', help=f"公共文件路径，用于自动替换json中的[{PLACEHOLDER_GLOBAL_PATH}]", type=str, required=True)
@click.option('--simg_path', '-s', help=f"singulartiy镜像路径，用于自动替换json中的[{PLACEHOLDER_SIMG_PATH}]", type=str, required=True)
@click.option('--runtimes', '-r', help=f"配置当前服务支持的自定义RUNTIME属性，多个属性之间使用逗号分隔", type=str)
def add(**kw):
    """新增自定义Cromwell Backend Host。用于添加一些自定义、用于测试的Cromwell Host
    {host, global_path, simg_path, backend: platform}
    """
    config = Config()

    if kw['runtimes']:
        kw['runtimes'] = kw['runtimes'].split(',')
    if kw['host']:
        kw['host'] = kw['host'].strip('/')
    cfg = {k: kw[k] for k in kw if kw[k]}
    if not kw['alias']:
        kw['alias'] = kw['backend']

    config.api.add_update_backend(cfg)

@cli.command()
def ls(**kw):
    """查看预设和个人自定义的backend配置
    """
    config = Config()
    # 每次查询都尝试覆盖本地数据
    config.init_backends()
    print("\t".join(["Owner", "Alias", "Backend", "Label", "Host", "Global_Database_Path", "SIMG_Path", "Runtimes"]))
    backends = config.api.get_backends()
    for backend in backends:
        print("\t".join([str(backend.get(k, '-')) for k in ['owner', 'alias', 'backend', 'label', 'host',  'global_path', 'simg_path', 'runtimes']]))

@cli.command()
@click.option("--alias", "-a", help="配置别名", required=True)
def delete(alias: str):
    """删除Cromwell Backend平台配置。（只能删除自定义的内容）"""
    config = Config()
    config.api.delete_backend(alias)
    # if not alias:
        # click.secho("删除出错，没有当前名称的配置项", fg='red', file=sys.stderr)
        # return 

    # config.del_server(alias)
    # config.pp(config.servers)

    # if not config.api:
    #     return

    # api = WDLAPI()
    # if pre_service:
    #     api.delete_backend(pre_service)
