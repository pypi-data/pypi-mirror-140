class SliceFilter(object):
    pass

class EntityPercentFilter(SliceFilter):
    # The lower limit allowed for percents of entities to filter through (out of a 100)
    # The percent must be greater than or equal to this limit
    LOWER_LIMIT = 0.1
    # The upper limit allowed for percents of entities to filter through (out of a 100).
    # The percent must be less than or equal to this limit
    UPPER_LIMIT = 100.0

    def __init__(self, percent: float):
        """
        Initializes an entity percent filter. Only one filter is allowed per query request.

        Args:
            percent (float): The percent of entities to filter.
                             Must be GTE to LOWER_LIMIT and LTE to UPPER_LIMIT.
        """
        if percent < EntityPercentFilter.LOWER_LIMIT or percent > EntityPercentFilter.UPPER_LIMIT:
            raise Exception("percent must be between {} and {}".format(EntityPercentFilter.LOWER_LIMIT, EntityPercentFilter.UPPER_LIMIT))
        super().__init__()
        self.percent = percent

    def get_percent(self) -> float:
        """
        Returns the percent of entities to filter

        Returns:
            float: The percent between (0, 100)
        """
        return self.percent
