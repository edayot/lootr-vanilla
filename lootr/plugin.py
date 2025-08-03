from typing import Any
from beet import Context
from beet.contrib.vanilla import Vanilla
from model_resolver.utils import resolve_key
from copy import deepcopy
from nbtlib import Compound, parse_nbt
from nbtlib.tag import List, Double
from nbtlib.contrib.minecraft.structure import StructureFileData
from tqdm import tqdm


def process_palette(palette: list[Any], key: str):
    to_replace: dict[int, int] = {}
    chest_compound = None
    for index, block in enumerate(deepcopy(palette)):
        block_id = resolve_key(block["Name"])
        if block_id == "minecraft:chest":
            if not chest_compound:
                # add an entry for chest
                chest_compound = len(palette)
                palette.append(parse_nbt('{Name: "minecraft:barrel", "Properties": {"facing":"up", "open": "false"}}'))
            to_replace[index] = chest_compound            
        if block_id == "minecraft:barrel":
            # use the same for barrel
            to_replace[index] = index

    return to_replace


def replace_blocks(data: StructureFileData, to_replace: dict[int, int]):
    if len(to_replace) == 0:
        return
    for block in data["blocks"]:
        block: StructureFileData.Block
        if (state := block.get("state")) not in to_replace:
            continue
        if not (nbt := block.get("nbt")):
            continue
        if not (loot_table := nbt.get("LootTable")):
            continue
        block["state"] = to_replace[state]
        del nbt["LootTable"]
        nbt["components"] = parse_nbt(f'{{"minecraft:custom_data": {{lootr: {{loot_table: "{loot_table}"}} }}}}')

        blockPos = deepcopy(block["pos"])
        pos = List[Double](float(x) + 0.5 for x in blockPos)

        data["entities"].append(Compound({
            "blockPos": blockPos,
            "pos": pos,
            "nbt": parse_nbt("""
{
    teleport_duration: 0,
    glow_color_override: -1,
    Tags: [
        "lootr.barrel"
    ],
    shadow_radius: 0f,
    transformation: {
        translation: [
        0f,
        0f,
        0f
        ],
        right_rotation: [
        0f,
        0f,
        0f,
        1f
        ],
        scale: [
        1f,
        1f,
        1f
        ],
        left_rotation: [
        0f,
        0f,
        0f,
        1f
        ]
    },
    OnGround: 0b,
    Air: 300s,
    view_range: 1f,
    id: "minecraft:item_display",
    UUID: [I;880652190,420630423,-1759317509,53559666],
    height: 0f,
    Motion: [
        0.0,
        0.0,
        0.0
    ],
    Invulnerable: 0b,
    billboard: "fixed",
    interpolation_duration: 0,
    width: 0f,
    shadow_strength: 1f,
    item_display: "none",
    Rotation: [
        0f,
        0f
    ],
    Pos: [
        -1709.5,
        120.0,
        494.5
    ],
    Fire: 0s,
    fall_distance: 0.0,
    PortalCooldown: 0
}
""")
        }))



def beet_default(ctx: Context):
    vanilla = ctx.inject(Vanilla)

    for key, structure in tqdm(deepcopy(vanilla.data.structures.items())):
        if paletes := structure.data.get("palettes"):
            to_replace = {}
            for palette in paletes:
                to_replace = process_palette(palette, key)
            replace_blocks(structure.data, to_replace)
        elif palette := structure.data.get("palette"):
            to_replace = process_palette(palette, key)
            replace_blocks(structure.data, to_replace)
        else:
            continue
        if len(to_replace) > 0:
            ctx.data.structures[key] = structure




