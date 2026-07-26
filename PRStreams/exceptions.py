class InvalidHash(Exception):
    message = "The link hash is invalid or has expired."


class FileNotFound(Exception):
    message = "The requested file no longer exists."
