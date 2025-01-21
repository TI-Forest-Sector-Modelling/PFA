from PNV.user_input.default_parameters import USER_INPUT, TOOLBOX_INPUT, SRC_CRS, DST_CRS
from PNV.src.logic import ProcessingArea
from PNV.toolbox.data_analysis import PnvDataAnalysis


def launch_toolbox(user_input: dict):
    """
    Launches the toolbox to validate and visualize aggregated data.
    :param user_input: Dictionary holding all user inputs.
    """

    pnv_analysis = PnvDataAnalysis(user_input=user_input)
    pnv_analysis.toolbox_plot()


def main(plot_fig: bool):
    """
    Main entry point for PNV project.
    :param plot_fig: Flag indicating whether to validate and visualize aggregated data.
    """
    preprocessing = ProcessingArea()
    if plot_fig:
        launch_toolbox(user_input=TOOLBOX_INPUT)


if __name__ == "__main__":
    main(plot_fig=True)

