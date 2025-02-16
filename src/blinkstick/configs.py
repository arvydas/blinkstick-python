from blinkstick.enums import BlinkStickVariant
from blinkstick.models import Configuration

_VARIANT_CONFIGS: dict[BlinkStickVariant, Configuration] = {
    BlinkStickVariant.BLINKSTICK: Configuration(
        mode_change_support=False,
    ),
    BlinkStickVariant.BLINKSTICK_PRO: Configuration(
        mode_change_support=True,
    ),
    BlinkStickVariant.BLINKSTICK_NANO: Configuration(
        mode_change_support=True,
    ),
    BlinkStickVariant.BLINKSTICK_SQUARE: Configuration(
        mode_change_support=True,
    ),
    BlinkStickVariant.BLINKSTICK_STRIP: Configuration(
        mode_change_support=True,
    ),
    BlinkStickVariant.BLINKSTICK_FLEX: Configuration(
        mode_change_support=True,
    ),
    BlinkStickVariant.UNKNOWN: Configuration(
        mode_change_support=False,
    ),
}


def _get_device_config(variant: BlinkStickVariant) -> Configuration:
    """Get the configuration for a BlinkStick variant"""
    return _VARIANT_CONFIGS.get(variant, _VARIANT_CONFIGS[BlinkStickVariant.UNKNOWN])
