from beet import Context
from simple_item_plugin.types import NAMESPACE, Lang
from simple_item_plugin.item import Item
from simple_item_plugin.crafting import ShapedRecipe, VanillaItem


def beet_default(ctx: Context):
    grappling_hook = Item(
        id="grappling_hook",
        base_item="minecraft:crossbow",
        item_name=(
            f"{NAMESPACE}.item.grappling_hook",
            {Lang.en_us: "Normal Grappling hook", Lang.fr_fr: "Grapin normal"},
        ),
        guide_description=(f"{NAMESPACE}.guide.normal", {
            Lang.en_us: "The normal grappling hook.",
            Lang.fr_fr: "Le grappin normal."
        })
    ).export(ctx)

    guide = Item(
        id="guide",
        base_item="minecraft:written_book",
        item_name=(
            f"{NAMESPACE}.item.guide",
            {Lang.en_us: "Guide", Lang.fr_fr: "Guide"},
        ),
        components_extra={
            "minecraft:enchantment_glint_override": False,
            "special:item_modifier": f"{NAMESPACE}:impl/guide",
        },
        guide_description=(f"{NAMESPACE}.guide.description", {
            Lang.en_us: "The guide you are currently holding.",
            Lang.fr_fr: "Le guide que vous tenez actuellement."
        })
    ).export(ctx)

    crossbow = VanillaItem(id="minecraft:crossbow")
    slimeball = VanillaItem(id="minecraft:slime_ball")

    ShapedRecipe(
        items=(
            (crossbow, slimeball, None),
            (slimeball, slimeball, None),
            (None, None, None),
        ),
        result=(grappling_hook, 1),
        flags=["consume_tools"],
    ).export(ctx)


