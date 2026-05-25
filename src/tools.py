"""Custom tools used by the LangGraph agent."""


def get_product_details(product_name: str) -> str:
    """Gathers basic details about a product.

    Args:
        product_name: Name of the product (e.g. headphones, shoes).

    Returns:
        Product description text, or a not-found message.
    """
    details = {
        "smartphone": (
            "A cutting-edge smartphone with advanced camera features "
            "and lightning-fast processing."
        ),
        "coffee": "A rich, aromatic blend of ethically sourced coffee beans.",
        "shoes": (
            "High-performance running shoes designed for comfort, "
            "support, and speed."
        ),
        "headphones": (
            "Wireless headphones with advanced noise cancellation "
            "technology for immersive audio."
        ),
        "speaker": (
            "A voice-controlled smart speaker that plays music, sets alarms, "
            "and controls smart home devices."
        ),
    }
    return details.get(product_name, "Product details not found.")
