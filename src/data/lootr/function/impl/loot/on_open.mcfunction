advancement revoke @s only lootr:impl/on_open

# Save player uuid
data modify storage lootr:main temp set value {}
data modify storage lootr:main temp.UUID set from entity @s UUID

function ~/on_hit:
    execute unless data block ~ ~ ~ components.minecraft:custom_data.lootr run return fail
    data modify block ~ ~ ~ lock set value {items:["minecraft:diamond"]}
    setblock ~ ~1 ~ gold_block

    function ~/set_current_player with storage lootr:main temp
    function ~/set_current_player:
        $data modify block ~ ~ ~ components.minecraft:custom_data.lootr.last_player set value "$(UUID)"

    function ~/choose with block ~ ~ ~ components.minecraft:custom_data.lootr
    function ~/choose:
        scoreboard players set #is_in_db lootr.math 0
        $execute \
            if data block ~ ~ ~ components.minecraft:custom_data.lootr.database."$(last_player)" \
            run return run data modify block ~ ~ ~ Items set from block ~ ~ ~ components.minecraft:custom_data.lootr.database."$(last_player)"



        function ~/loot with block ~ ~ ~ components.minecraft:custom_data.lootr
        function ~/loot:
            data modify block ~ ~ ~ Items set value []
            $loot insert ~ ~ ~ loot $(loot_table)



execute anchored eyes positioned ^ ^ ^ run function #bs.raycast:run {with:{
    on_targeted_block: f"function {~/on_hit}",
}}




