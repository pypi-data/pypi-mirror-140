from .cromwell import cli as cromwell_cli
from .monitor import cli as monitor_cli
from .adaptor import cli as adaptor_cli
from .api import cli as server_cli
from .base import AliasedGroup
from yucebio.yc2.adaptor.util.config import Config
import click


@click.group(cls=AliasedGroup)
def cli():
    """WDL 适配器

    - 转换通用WDL到特定平台\n
    - 任务查看、管理
    """
    pass

@cli.command()
@click.option('--api', '-a', help="YC2 API地址", required=True, type=str, default="http://yc2.yucebio.com")
def set_api(api):
    """修改和设置YC2 API地址
    """
    c = Config()
    if api:
        c.set('api', api)
        c.reload()
    print("CURRENT API:", c.get('api'))

@cli.command()
@click.option("--username", '-u', help="用户名", required=True, type=str)
@click.password_option("--password", '-p', help="密码")
def login(username, password):
    """登录"""
    c = Config(check_user=False)
    try:
        c.login(username, password)
    except Exception as e:
        raise click.exceptions.ClickException(f"{e}")
    click.secho(f"Hi {username}! Welcome to Yucebio WDL!!!", fg='green')

# cli.add_command(login, 'login')
# cli.add_command(config_cli, 'config')
cli.add_command(cromwell_cli, 'cromwell')
cli.add_command(monitor_cli, 'monitor')
cli.add_command(adaptor_cli, 'adaptor')
cli.add_command(server_cli, 'api')

@cli.command()
def version():
    """显示版本信息
    """
    from yucebio.yc2.adaptor.version import __version__
    print("Version: ", __version__)
    c = Config(check_user=False)
    print("Config File:", c.configfile)



