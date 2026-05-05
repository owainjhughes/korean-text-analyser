class RedirectToLogin(Exception):
    """Raised by HTML route deps when the user isn't authenticated.

    Caught at app level and converted to a 303 redirect to /login?next=<path>.
    """

    def __init__(self, next_path: str) -> None:
        self.next_path = next_path
        super().__init__(f"redirect to /login?next={next_path}")
