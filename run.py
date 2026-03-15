from __future__ import annotations

from src.app_ui import StreamlitUI


def main() -> None:
    """Entry point for the Streamlit application."""
    ui = StreamlitUI()
    ui.run()


if __name__ == "__main__":
    main()