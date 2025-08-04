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
    data_mode: set[int] = set()
    chest_compound = len(palette)
    palette.append(parse_nbt('{Name: "minecraft:barrel", "Properties": {"facing":"up", "open": "false"}}'))
    for index, block in enumerate(deepcopy(palette)):
        block_id = resolve_key(block["Name"])
        if block_id == "minecraft:chest":
            to_replace[index] = chest_compound            
        if block_id == "minecraft:barrel":
            # use the same for barrel
            to_replace[index] = index
        if block_id == "minecraft:structure_block":
            mode = block["Properties"]["mode"]
            if mode == "data":
                data_mode.add(index)
    return to_replace, data_mode, chest_compound


def replace_data_mode(data: StructureFileData, data_mode: set[int], key: str, chest_compound: int):
    if len(data_mode) == 0:
        return False
    # set of indexs to delete in the list
    to_delete: set[int] = set()
    to_modify: dict[tuple[int, ...], str] = {}

    for index, block in enumerate(data["blocks"]):
        block: StructureFileData.Block
        if (state := block.get("state")) not in data_mode:
            continue
        if not (nbt := block.get("nbt")):
            continue
        if not (metadata := nbt.get("metadata")):
            continue
        if resolve_key(key) == "minecraft:igloo/bottom":
            if metadata == "chest":
                to_delete.add(index)
                blockPos = deepcopy(block["pos"])
                blockPos = tuple(int(x) for x in blockPos)
                assert len(blockPos) == 3
                blockPos = (blockPos[0], blockPos[1] - 1, blockPos[2])
                to_modify[blockPos] = "minecraft:chests/igloo_chest"
    
    for index, block in enumerate(data["blocks"]):
        block: StructureFileData.Block
        blockPos = deepcopy(block["pos"])
        blockPos = tuple(int(x) for x in blockPos)
        if blockPos in to_modify:
            to_delete.add(index)
    
    for i in sorted(to_delete, reverse=True):
        del data["blocks"][i]
    
    for blockPos, loot_table in to_modify.items():
        block = StructureFileData.Block({
            "state": chest_compound,
            "pos": blockPos,
            "nbt": parse_nbt(f'{{"minecraft:custom_data": {{lootr: {{loot_table: "{loot_table}"}} }}}}')
        })
        data["blocks"].append(block)
    return True
    

def add_entity(data: StructureFileData, blockPos: tuple[int, ...]):
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

def replace_blocks(data: StructureFileData, to_replace: dict[int, int]) -> bool:
    res = False
    if len(to_replace) == 0:
        return False
    for block in data["blocks"]:
        block: StructureFileData.Block
        if (state := block.get("state")) not in to_replace:
            continue
        if not (nbt := block.get("nbt")):
            continue
        if not (loot_table := nbt.get("LootTable")):
            continue
        res = True
        block["state"] = to_replace[state]
        del nbt["LootTable"]
        nbt["components"] = parse_nbt(f'{{"minecraft:custom_data": {{lootr: {{loot_table: "{loot_table}"}} }}}}')

        blockPos = deepcopy(block["pos"])
        blockPos = tuple(int(x) for x in blockPos)
        add_entity(data, blockPos)
    return res



def beet_default(ctx: Context):
    vanilla = ctx.inject(Vanilla)

    for key, structure in tqdm(deepcopy(vanilla.data.structures.items())):
        success: list[bool] = []
        if paletes := structure.data.get("palettes"):
            to_replace = {}
            data_mode: set[int] = set()
            chest_compound = None
            for palette in paletes:
                to_replace, data_mode, chest_compound = process_palette(palette, key)
            if chest_compound is None:
                raise ValueError(f"Need at least one palette in palletes : {key}")
            success.append(replace_blocks(structure.data, to_replace))
            success.append(replace_data_mode(structure.data, data_mode, key, chest_compound))
        elif palette := structure.data.get("palette"):
            to_replace, data_mode, chest_compound = process_palette(palette, key)
            success.append(replace_blocks(structure.data, to_replace))
            success.append(replace_data_mode(structure.data, data_mode, key, chest_compound))
        else:
            continue
        if any(success):
            ctx.data.structures[key] = structure




