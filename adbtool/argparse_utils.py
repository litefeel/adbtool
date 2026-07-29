import argparse


class CommaSeparatedAppendAction(argparse.Action):
    """Append repeated option values and expand comma-separated items."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | None,
        option_string: str | None = None,
    ) -> None:
        items = getattr(namespace, self.dest, None)
        if items is None:
            items = []

        if values is None:
            setattr(namespace, self.dest, items)
            return

        values_to_add = [value.strip() for value in values.split(",")]
        if any(not value for value in values_to_add):
            raise argparse.ArgumentError(
                self,
                f"{option_string or self.dest} contains an empty comma-separated value",
            )

        items.extend(values_to_add)
        setattr(namespace, self.dest, items)
