import click


def _print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("0.0.0")
    ctx.exit()


def _print_pretty_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("0.0.0")
    ctx.exit()


@click.group()
@click.option(
    '--version',
    is_flag=True,
    callback=_print_version,
    expose_value=False,
    is_eager=True,
    help="""
    Prints version in short format.
    """
)
@click.option(
    '--version-info',
    is_flag=True,
    callback=_print_pretty_version,
    expose_value=False,
    is_eager=True,
    help="""
    Prints version in long format, providing more details.
    """
)
def lab():
    """
    Looker Aggregate Builder command line interface, a tool for boosting Looker LookML developments.
    """
    pass    # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    lab()
