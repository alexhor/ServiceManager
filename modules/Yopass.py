#!/usr/bin/python3

from .Module import Module


class Yopass(Module):
    """
    A Yopass instance.

    Yopass can be used to securely share secrets via one-use links
    """

    def __init__(self, subDomain):
        self.requiredDirs = []
        super().__init__(subDomain)
        # Does not require special configuration
