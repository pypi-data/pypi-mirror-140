"""General Error classes for OncoPlot Extractor"""


class OncoPlotExtractorError(Exception):
    """Base class for all OncoPlot Extractor errors."""

    def __init__(self, msg) -> None:
        super().__init__(msg)
