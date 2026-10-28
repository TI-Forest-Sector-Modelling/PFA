from pathlib import Path
import click
from PNV.user_input.default_parameters import USER_INPUT, TOOLBOX_INPUT
from PNV.main import main
from PNV.src.defines import ParamNames

@click.group()
def cli():
    pass


@cli.command("run")
@click.option(
    '-PD', f'--{ParamNames.process_data.value}', f'{ParamNames.process_data.value}',
    default=USER_INPUT[ParamNames.process_data.value],
    show_default=True,
    required=True,
    type=bool,
    help="Process input data."
)
@click.option(
    '-CS', f'--{ParamNames.class_selection.value}', f'{ParamNames.class_selection.value}',
    default=USER_INPUT[ParamNames.class_selection.value],
    show_default=True,
    required=True,
    type=int,
    help="Selected number of classes."
)
@click.option(
    '-PM', f'--{ParamNames.plot_maps.value}', f'{ParamNames.plot_maps.value}',
    default=USER_INPUT[ParamNames.plot_maps.value],
    show_default=True, required=True, type=bool,
    help="Flag to plot maps for generated data."
)
@click.option(
    '-PDF', f'--{ParamNames.plot_downscale_factor.value}', f'{ParamNames.plot_downscale_factor.value}',
    default=USER_INPUT[ParamNames.plot_downscale_factor.value],
    show_default=True,
    required=True,
    type=int,
    help="Factor to downscale plotted maps to reduce computation load."
)
@click.option(
    '-MA', f'--{ParamNames.merge_agri_data.value}', f'{ParamNames.merge_agri_data.value}',
    default=USER_INPUT[ParamNames.merge_agri_data.value],
    show_default=True,
    required=True,
    type=bool,
    help='Flag to merge agri data.'
)
@click.option(
    '-YA', f'--{ParamNames.year_agri_data.value}', f'{ParamNames.year_agri_data.value}',
    default=USER_INPUT[f'{ParamNames.year_agri_data.value}'],
    show_default=True,
    required=True,
    type=int,
    help='Select year of agricultural data (2015 or 2020).'
)
@click.option(
    '-GF', f'--{ParamNames.generate_fig.value}', f'{ParamNames.generate_fig.value}',
    default=USER_INPUT[ParamNames.generate_fig.value],
    show_default=True,
    required=True,
    type=bool,
    help="Flag to generate additional figures."
)
@click.option(
    '-GG', f'--{ParamNames.generate_gif.value}', f'{ParamNames.generate_gif.value}',
    default=USER_INPUT[ParamNames.generate_gif.value],
    show_default=True,
    required=True,
    type=bool,
    help='Flag to generate GIF images.'
)
@click.option(
    '-CGL', f'--{ParamNames.calc_gain_loss.value}', f'{ParamNames.calc_gain_loss.value}',
    default=USER_INPUT[ParamNames.calc_gain_loss.value],
    show_default=True,
    required=True,
    type=bool,
    help='Flag to calculate area gains and losses via cross-scenario analysis.'
)
def pfa_cli(process_data, class_selection, plot_maps, plot_downscale_factor, merge_agri_data, year_agri_data,
            generate_fig, generate_gif, calc_gain_loss_loss):
    """starts PFA model"""
    cli_pj_user_input = {
        ParamNames.process_data.value: process_data,
        ParamNames.class_selection.value: class_selection,
        ParamNames.plot_maps.value: plot_maps,
        ParamNames.plot_downscale_factor.value: plot_downscale_factor,
        ParamNames.zipped_data.value: USER_INPUT[ParamNames.zipped_data.value],
        ParamNames.merge_agri_data.value: merge_agri_data,
        ParamNames.year_agri_data.value: year_agri_data,
        ParamNames.generate_fig.value: generate_fig,
        ParamNames.generate_gif.value: generate_gif,
        ParamNames.calc_gain_loss.value: calc_gain_loss_loss
    }

    cli_tb_user_input = {
        ParamNames.class_selection.value: class_selection,
        ParamNames.merge_agri_data.value: merge_agri_data,
        ParamNames.select_year.value: TOOLBOX_INPUT[ParamNames.select_year.value],
        ParamNames.select_rcp.value: TOOLBOX_INPUT[ParamNames.select_rcp.value],
        ParamNames.select_agg_lvl.value: TOOLBOX_INPUT[ParamNames.select_agg_lvl.value],
        ParamNames.select_iso.value: TOOLBOX_INPUT[ParamNames.select_iso.value],
        ParamNames.rel_val_tolerance.value: TOOLBOX_INPUT[ParamNames.rel_val_tolerance.value],
        ParamNames.paper_format.value: TOOLBOX_INPUT[ParamNames.paper_format.value],
        ParamNames.save_figure.value: TOOLBOX_INPUT[ParamNames.save_figure.value],
        ParamNames.output_name.value: TOOLBOX_INPUT[ParamNames.output_name.value]
    }

    main(pj_user_input=cli_pj_user_input, tb_user_input=cli_tb_user_input)

