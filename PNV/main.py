from PNV.user_input.default_parameters import USER_INPUT, TOOLBOX_INPUT
from PNV.src.logic import ProcessingArea
from PNV.toolbox.data_analysis import PnvDataAnalysis
from PNV.src.defines import ParamNames


def launch_toolbox(tb_user_input: dict, pj_user_input: dict):
    """
    Launches the toolbox to validate and visualize aggregated data.
    :param tb_user_input: Dictionary holding all user inputs for toolbox
    :param pj_user_input: Dictionary holding all user inputs for project
    """

    pnv_analysis = PnvDataAnalysis(tb_user_input=tb_user_input, pj_user_input=pj_user_input)
    if pj_user_input[ParamNames.generate_fig.value]:
        pnv_analysis.toolbox_plot()
    if pj_user_input[ParamNames.generate_gif.value]:
        pnv_analysis.toolbox_gif()


def main(pj_user_input: dict, tb_user_input: dict):
    """
    Main entry point for PFA project.
    """
    preprocessing = ProcessingArea(pj_user_input=pj_user_input)
    launch_toolbox(tb_user_input=tb_user_input, pj_user_input=pj_user_input)


if __name__ == "__main__":
    main(pj_user_input=USER_INPUT, tb_user_input=TOOLBOX_INPUT)

