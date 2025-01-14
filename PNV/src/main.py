from PNV.user_input.default_parameters import USER_INPUT, TOOLBOX_INPUT, SRC_CRS, DST_CRS
from PNV.src.logic import ProcessingArea
from PNV.toolbox.data_analysis import PnvDataAnalysis


def launch_toolbox(user_input: dict):

    pnv_analysis = PnvDataAnalysis(user_input=user_input)
    pnv_analysis.toolbox_plot()


def main(plot_fig: bool):
    preprocessing = ProcessingArea()
    if plot_fig:
        launch_toolbox(user_input=TOOLBOX_INPUT)


if __name__ == "__main__":
    main(plot_fig=True)

