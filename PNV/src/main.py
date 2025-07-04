from PNV.user_input.default_parameters import USER_INPUT, TOOLBOX_INPUT, SRC_CRS, DST_CRS
from PNV.src.logic import ProcessingArea
from PNV.toolbox.data_analysis import PnvDataAnalysis


def launch_toolbox(tb_user_input: dict, pj_user_input: dict):
    """
    Launches the toolbox to validate and visualize aggregated data.
    :param tb_user_input: Dictionary holding all user inputs for toolbox
    :param pj_user_input: Dictionary holding all user inputs for project
    """

    pnv_analysis = PnvDataAnalysis(tb_user_input=tb_user_input, pj_user_input=pj_user_input)
    if pj_user_input['GENERATE_FIG']:
        pnv_analysis.toolbox_plot()
    if pj_user_input['GENERATE_GIF']:
        pnv_analysis.toolbox_gif()


def main():
    """
    Main entry point for PNV project.
    """
    preprocessing = ProcessingArea()
    launch_toolbox(tb_user_input=TOOLBOX_INPUT, pj_user_input=USER_INPUT)


if __name__ == "__main__":
    main()

